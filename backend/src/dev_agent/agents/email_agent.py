"""
EmailAgent — refactored & calibrated with backward compatibility hooks.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Awaitable, Callable, Literal, Optional, List

from groq import AsyncGroq
from pydantic import BaseModel, field_validator

from dev_agent.agents.base_agent import BaseAgent
from dev_agent.core.config import get_settings
from dev_agent.core.models import AgentResult, AgentType
from dev_agent.tools.email.reader import GmailReader
from dev_agent.tools.email.sender import GmailSender

logger = logging.getLogger(__name__)

TokenRefreshCallback = Callable[[], Awaitable[str]]

# ---------------------------------------------------------------------------
# Schema de classificação retornado pelo LLM
# ---------------------------------------------------------------------------

class EmailIntent(BaseModel):
    intent: Literal["send", "draft", "read"]
    recipient: Optional[str] = None   # só para "send"
    subject: Optional[str] = None     # só para "send"
    body: Optional[str] = None        # só para "send" e "draft"
    reasoning: str                    # justificação curta

    @field_validator("recipient")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.fullmatch(r"[\w.+-]+@[\w-]+\.\w+", v):
            raise ValueError(f"Email inválido: {v}")
        return v


# ---------------------------------------------------------------------------
# Prompt de classificação (Calibrado)
# ---------------------------------------------------------------------------

_CLASSIFY_SYSTEM = """\\
You are an email intent classifier. Given a user query about email, respond ONLY with valid JSON.

Output format:
{
  "intent": "send" | "draft" | "read",
  "recipient": "<email address or null>",
  "subject": "<subject line or null>",
  "body": "<email body or null>",
  "reasoning": "<one sentence>"
}

Rules:
- "send"  → The user explicitly and imperatively wants to transmit/dispatch/deliver an email RIGHT NOW (e.g., "envie", "enviar", "mande para", "dispare"). It MUST have a clear recipient email address and a final text body.
  - Explicit dispatch phrasing like "envie esta sugestão", "podes enviar o rascunho", "manda o rascunho", "dispare isso", or "envia isto" is always "send".
- "draft" → The user wants to compose, write, suggest, or generate a response text, proposal, or draft (e.g., "gere uma proposta", "escreva uma resposta", "sugira um texto", "crie um rascunho"). Even if a recipient email is present in the prompt, if the action verbs are about "generating/suggesting/writing/proposing", it is ALWAYS a "draft", NOT a "send".
- "read"  → The user wants to read, view, list, search, or analyse their inbox.

Crucial Instruction:
- The 'recipient' field MUST contain only a valid structured email address (containing '@' and a domain). If the user provides only a name (e.g., "Eduardo Carvalho") or references like "him", "her", or "ele", leave the 'recipient' field strictly as null or empty (O campo 'recipient' DEVE conter apenas um endereço de e-mail estruturado válido com '@' e domínio. Se o utilizador fornecer apenas um nome próprio ou referências como 'ele', deixa o campo 'recipient' estritamente como null ou vazio).
- If the user uses words like "proposta", "sugestão", "rascunho", "draft", "escreva uma resposta" or "como responder", the intent is STRICTLY "draft" unless the user gives a direct command to dispatch the message immediately.
- If the user asks to send but the recipient or body are not explicit in the current query, return null for those fields and include reasoning that the agent should infer the last referenced email from session context or ask the user to confirm the missing recipient/body. Do not invent placeholder addresses or reply with a generic example command.

Respond with ONLY the JSON object — no markdown, no extra text.
"""


_EXTRACTION_SYSTEM = """You are an email context extractor.
Analyze the user's previous query and the assistant's previous response to extract:
1. The recipient's email address (must be a valid email containing '@' and domain, e.g. 'eduardo.carvalho@gmail.com').
2. The subject of the email (if mentioned or can be inferred).
3. The body/content of the email (the full text of the message/draft/recipe generated).

Respond ONLY with valid JSON.
Output format:
{
  "recipient": "<email or null>",
  "subject": "<subject or null>",
  "body": "<body or null>"
}
"""


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class EmailAgent(BaseAgent):
    agent_type = AgentType.EMAIL

    def __init__(
        self,
        token: str | None,
        on_token_refresh: Optional[TokenRefreshCallback] = None,
        github_repositories: Optional[list] = None,
    ) -> None:
        self.token = token
        self.on_token_refresh = on_token_refresh
        # Optional context injected by the Orchestrator/Dispatcher
        self.github_repositories = github_repositories
        self.settings = get_settings()
        self.client = AsyncGroq(api_key=self.settings.groq_api_key)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    async def run(self, query: str, history: Optional[List[dict]] = None) -> AgentResult:
        if not self.token:
            return self.failure("Gmail não está ligado. Liga a tua conta primeiro.")

        intent = await self._classify(query, history=history)
        if intent is None:
            return self.failure("Não consegui interpretar o pedido. Tenta ser mais específico.")

        logger.debug("EmailAgent intent=%s reasoning=%s", intent.intent, intent.reasoning)

        # 1. Creative or general generation flow (ex: recipes, textos do zero, piadas)
        if self._is_creative_or_general_generation(query):
            return await self._handle_creative_generation(query, intent, history=history)

        match intent.intent:
            case "send":
                return await self._handle_send(intent, query, history=history)
            case "draft":
                return await self._handle_draft(query, intent)
            case "read":
                return await self._handle_read(query)

    # ------------------------------------------------------------------
    # Intent classification (single LLM call)
    # ------------------------------------------------------------------

    async def _classify(self, query: str, history: Optional[List[dict]] = None) -> Optional[EmailIntent]:
        for attempt in range(2):
            try:
                messages = [{"role": "system", "content": _CLASSIFY_SYSTEM}]
                if history:
                    # history is sorted descending (newest first). Take up to 4 messages and reverse.
                    recent_history = history[:4]
                    for msg in reversed(recent_history):
                        messages.append({
                            "role": msg.get("role"),
                            "content": msg.get("content")
                        })
                messages.append({"role": "user", "content": query})

                resp = await self.client.chat.completions.create(
                    model=self.settings.groq_model,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=300,
                )
                raw = resp.choices[0].message.content or ""
                data = json.loads(raw)
                return EmailIntent(**data)
            except (json.JSONDecodeError, ValueError) as exc:
                logger.warning("Classify attempt %d failed: %s", attempt + 1, exc)

        return None

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def _handle_creative_generation(self, query: str, intent: EmailIntent, history: Optional[List[dict]] = None) -> AgentResult:
        logger.debug("Creative or general generation query detected: %s", query)
        
        # 1. Retrieve recipient (direct from intent or query extract)
        recipient = intent.recipient
        if not recipient and query:
            recipient = self._extract_email_address(query)
            
        # Validate recipient against outgoing anti-spam filter if present
        if recipient and not self._is_valid_human_email(recipient):
            recipient = None

        # 2. Fallback to history turn memory inheritance if query is confirmation and history is present
        if not recipient:
            if history and self._is_confirmation_query(query):
                extracted = await self._extract_from_previous_turn(history)
                if extracted and extracted.get("recipient"):
                    ext_recip = extracted.get("recipient")
                    if self._is_valid_human_email(ext_recip):
                        recipient = ext_recip
                        logger.debug("Herdado recipient do histórico para fluxo criativo: %s", recipient)

        # 3. Determine if intent is send or draft
        # If a recipient is specified or intent is send, we want to send it.
        is_send = (intent.intent == "send") or bool(recipient) or bool(re.search(r"\b(envie|enviar|mande|mandar|dispare|disparar|envia|manda)\b", query.lower()))

        # 4. Generate creative body using LLM knowledge directly (no inbox correlation!)
        body = intent.body
        body_str = (body or "").strip()
        if len(body_str) < 3:
            try:
                logger.debug("Generating creative/general email body directly using LLM...")
                body = await self._generate_creative_body(query)
                body = (body or "").strip()
            except Exception as exc:
                logger.exception("Erro ao gerar corpo criativo")
                return self.failure(f"Erro ao gerar corpo do email: {exc}")

        subject = intent.subject
        if not subject or subject.strip().lower() in ("", "sem assunto"):
            subject = "Conteúdo sugerido"

        if is_send:
            if not recipient:
                return self.failure(
                    "Não consegui resgatar o e-mail do destinatário no histórico. "
                    "Por favor, me informe o endereço correto para o envio."
                )
            
            try:
                sender = GmailSender(self.token, on_token_refresh=self.on_token_refresh)
                result = await sender.send_email(
                    to=recipient,
                    subject=subject,
                    body=body,
                )
                return self.success({
                    "action": "send",
                    "recipient": recipient,
                    "subject": subject,
                    "body_preview": body[:150],
                    "result": result,
                })
            except Exception as exc:
                logger.exception("Erro ao enviar email criativo")
                return self.failure(f"Erro ao enviar email: {exc}")
        else:
            return self.success({
                "action": "draft",
                "proposed_response": body,
                "instructions": (
                    "Sugestão gerada. Para enviar este texto, confirma o destinatário e o corpo no próximo pedido."
                ),
            })

    async def _handle_send(self, intent: EmailIntent, query: Optional[str] = None, history: Optional[List[dict]] = None) -> AgentResult:
        query_text = query or ""
        is_github_query = bool(re.search(r"\bgithub\b|\breposit[oó]rio", query_text, re.IGNORECASE))
        injected_repos = getattr(self, "github_repositories", None)

        recipient = intent.recipient
        if not recipient and query_text:
            recipient = self._extract_email_address(query_text)
        if recipient and not self._is_valid_human_email(recipient):
            recipient = None

        subject = intent.subject
        body = intent.body

        # 1. Creative or general generation flow (ex: recipes, textos do zero, piadas)
        if self._is_creative_or_general_generation(query_text):
            return await self._handle_creative_generation(query_text, intent, history=history)
        else:
            # 2. Regular inbox context correlation flow
            # Turn memory inheritance (if query is confirmation query and history is present)
            if history and self._is_confirmation_query(query_text):
                extracted = await self._extract_from_previous_turn(history)
                if extracted:
                    if not recipient and extracted.get("recipient"):
                        ext_recip = extracted.get("recipient")
                        if self._is_valid_human_email(ext_recip):
                            recipient = ext_recip
                            logger.debug("Herdado recipient do histórico: %s", recipient)
                    if (not subject or subject.strip().lower() in ("", "sem assunto")) and extracted.get("subject"):
                        subject = extracted.get("subject")
                        logger.debug("Herdado subject do histórico: %s", subject)
                    if (not body or len(body.strip()) < 3) and extracted.get("body"):
                        body = extracted.get("body")
                        logger.debug("Herdado body do histórico: %s", body)

            # Strict name matching in inbox (no blind fallback)
            selected_email = None
            if not recipient and query_text:
                try:
                    reader = GmailReader(self.token, on_token_refresh=self.on_token_refresh)
                    emails = await reader.get_recent_emails(max_results=15)
                    if emails:
                        for e in emails:
                            from_val = e.get("from") or ""
                            email_addr = self._extract_email_address(from_val)
                            if email_addr and self._is_valid_human_email(email_addr):
                                display_name = from_val.split("<")[0].replace('"', '').strip() if "<" in from_val else from_val.replace('"', '').strip()
                                if self._is_name_match(display_name, query_text):
                                    if is_github_query:
                                        is_eduardo_carvalho = (
                                            re.search(r"\beduardo\b", display_name, re.IGNORECASE) and 
                                            re.search(r"\bcarvalho\b", display_name, re.IGNORECASE)
                                        )
                                        if not is_eduardo_carvalho:
                                            continue
                                    recipient = email_addr
                                    selected_email = e
                                    logger.debug("Mapeado destinatário por correspondência de nome: %s", recipient)
                                    break
                except Exception as exc:
                    logger.debug("Não foi possível aceder ao histórico de emails para resolver nome: %s", exc)

            # Handle body and subject resolution
            if is_github_query and injected_repos:
                subject = subject or f"Resumo dos repositórios ({len(injected_repos)})"
                repos_list_text = "\n".join(f"- {r}" for r in injected_repos)
                body = (
                    f"Segue em baixo a lista de repositórios solicitados (fonte: GitHubAgent).\n\n{repos_list_text}\n\n"
                    "Este corpo foi gerado exclusivamente com base na lista de repositórios fornecida; nenhumas informações da caixa de entrada foram usadas."
                )
            else:
                if not subject or subject.strip().lower() in ("", "sem assunto"):
                    if selected_email:
                        orig_subject = selected_email.get("subject") or "Sem assunto"
                        if orig_subject.lower().startswith("re:"):
                            subject = orig_subject
                        else:
                            subject = f"Re: {orig_subject}"
                    else:
                        subject = "Sem assunto"

                body_str = (body or "").strip()
                if len(body_str) < 3:
                    if not selected_email and not is_github_query:
                        try:
                            reader = GmailReader(self.token, on_token_refresh=self.on_token_refresh)
                            emails = await reader.get_recent_emails(max_results=15)
                            if emails:
                                filtered_emails = []
                                for e in emails:
                                    email_addr = self._extract_email_address(e.get("from", ""))
                                    if email_addr and self._is_valid_human_email(email_addr):
                                        filtered_emails.append(e)
                                if filtered_emails:
                                    selected_email = self._pick_most_relevant(query_text, filtered_emails)
                        except Exception as exc:
                            logger.debug("Erro ao tentar buscar email relevante para regenerar corpo: %s", exc)

                    if selected_email:
                        try:
                            logger.debug("Corpo ausente. A regenerar corpo usando LLM.")
                            body = await self._regenerate_body(query_text or intent.reasoning or "", selected_email)
                            body = (body or "").strip()
                        except Exception as exc:
                            logger.exception("Erro ao regenerar corpo do email")
                            return self.failure(f"Erro ao gerar corpo do email: {exc}")

        # 3. Strict validation check
        if not recipient or not self._is_valid_human_email(recipient) or not body or len(body.strip()) < 3:
            return self.failure(
                "Não consegui resgatar o e-mail do destinatário no histórico. "
                "Por favor, me informe o endereço correto para o envio."
            )

        try:
            sender = GmailSender(self.token, on_token_refresh=self.on_token_refresh)
            result = await sender.send_email(
                to=recipient,
                subject=subject,
                body=body,
            )
            return self.success({
                "action": "send",
                "recipient": recipient,
                "subject": subject,
                "body_preview": body[:150],
                "result": result,
            })
        except Exception as exc:
            logger.exception("Erro ao enviar email")
            return self.failure(f"Erro ao enviar email: {exc}")

    async def _handle_draft(self, query: str, intent: EmailIntent) -> AgentResult:
        if self._is_creative_or_general_generation(query):
            return await self._handle_creative_generation(query, intent)

        q_low = query.lower()
        has_explicit_body = intent.body and len(intent.body.strip()) > 40
        is_requesting_generation = bool(
            re.search(r"\b(ger(ar|e|ando)|proposta|sugest(ão|ao)|rascunho|draft|resposta|como responder|escreva|escrever|sugira|sugerir)\b", q_low)
        )
        if has_explicit_body and not is_requesting_generation:
            return self.success({
                "action": "draft",
                "proposed_response": intent.body.strip(),
                "instructions": (
                    "Sugestão gerada. Para enviar este texto, confirma o destinatário e o corpo no próximo pedido."
                ),
            })

        # Se estivermos em modo GitHub com repositórios injetados, gere um rascunho baseado EXCLUSIVAMENTE nessa lista
        injected_repos = getattr(self, "github_repositories", None)
        is_github_query = bool(re.search(r"\bgithub\b|\breposit[oó]rio", query, re.IGNORECASE))
        if is_github_query and injected_repos:
            repos_list_text = "\n".join(f"- {r}" for r in injected_repos)
            draft_text = (
                f"Segue uma proposta de email com base na lista de repositórios fornecida:\n\n{repos_list_text}\n\n"
                "Nota: este rascunho foi gerado apenas a partir dos repositórios providenciados pelo GitHubAgent; nenhuma informação da inbox foi utilizada."
            )
            return self.success({
                "action": "draft",
                "context_from": "GitHubAgent",
                "context_subject": f"Resumo de {len(injected_repos)} repositórios",
                "proposed_response": draft_text,
                "instructions": (
                    "Sugestão gerada a partir dos repositórios; para enviar, confirma o destinatário e o corpo no próximo pedido."
                ),
            })

        try:
            reader = GmailReader(self.token, on_token_refresh=self.on_token_refresh)
            emails = await reader.get_recent_emails(max_results=15)
        except Exception as exc:
            logger.exception("Erro ao ler emails para draft")
            return self.failure(f"Erro ao aceder ao Gmail: {exc}")

        if not emails:
            return self.failure("Não há emails recentes na inbox para usar como contexto.")

        context_email = self._pick_most_relevant(query, emails)
        draft_text = await self._generate_draft(query, context_email)

        return self.success({
            "action": "draft",
            "context_from": context_email.get("from", "Desconhecido"),
            "context_subject": context_email.get("subject", "Sem assunto"),
            "proposed_response": draft_text,
            "instructions": (
                "Sugestão de resposta gerada. Para enviar, confirma o destinatário e o corpo no próximo pedido."
            ),
        })

    async def _handle_read(self, query: str) -> AgentResult:
        try:
            reader = GmailReader(self.token, on_token_refresh=self.on_token_refresh)
            emails = await reader.get_recent_emails(max_results=15)
        except Exception as exc:
            logger.exception("Erro ao ler emails")
            return self.failure(f"Erro ao aceder ao Gmail: {exc}")

        if not emails:
            return self.success({
                "action": "read",
                "emails_found": 0,
                "emails": [],
                "highlight": "Não há emails recentes na inbox.",
            })

        highlight = await self._summarise_relevant(query, emails)
        return self.success({
            "action": "read",
            "emails_found": len(emails),
            "emails": emails[:10],
            "highlight": highlight,
        })

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _pick_most_relevant(self, query: str, emails: list[dict]) -> dict:
        query_tokens = set(query.lower().split())
        best, best_score = emails[0], -1

        for email in emails[:10]:
            combined = (
                f"{email.get('from', '')} {email.get('subject', '')} {email.get('snippet', '')}"
            ).lower()
            score = sum(1 for token in query_tokens if token in combined)
            if score > best_score:
                best, best_score = email, score

        return best

    def _extract_email_address(self, text: str) -> Optional[str]:
        if not text:
            return None
        match = re.search(r"[\w.+-]+@[\w-]+\.\w+", text)
        return match.group(0) if match else None

    def _is_valid_human_email(self, email_addr: str) -> bool:
        if not email_addr:
            return False
        email_addr = email_addr.strip().lower()
        if not re.fullmatch(r"[\w.+-]+@[\w-]+\.\w+", email_addr):
            return False
        parts = email_addr.split("@")
        if len(parts) != 2:
            return False
        user_part, domain_part = parts[0], parts[1]
        
        # Strict anti-spam list: rejects temu, temuemail, teste, promo, spam, updates, no-reply, noreply, etc.
        rejected_keywords = [
            "reply", "notification", "daemon", "bounce", "alert", "system", 
            "support", "info", "news", "newsletter", "marketing", "billing",
            "bot", "no-reply", "noreply", "service", "automated", "status",
            "temu", "temuemail", "teste", "promo", "spam", "update", "offers", 
            "newsletter", "feed"
        ]
        
        for keyword in rejected_keywords:
            if keyword in user_part or keyword in domain_part:
                return False
        return True

    def _is_name_match(self, display_name: str, query: str) -> bool:
        if not display_name or not query:
            return False
        name_clean = display_name.split("<")[0].replace('"', '').strip().lower()
        if not name_clean:
            return False
        
        name_words = [w for w in re.findall(r"\b[a-zA-Z0-9áéíóúâêîôûãõçàèìòùäëïöüÿñ]+\b", name_clean) if len(w) >= 2]
        if not name_words:
            return False
            
        query_clean = query.lower()
        
        if len(name_words) >= 2:
            return all(word in query_clean for word in name_words)
            
        return any(rf"\b{re.escape(word)}\b" for word in name_words if re.search(rf"\b{re.escape(word)}\b", query_clean))

    def _is_creative_or_general_generation(self, query: str) -> bool:
        if not query:
            return False
        q = query.lower()
        creative_keywords = [
            r"\breceita\b", r"\bpiada\b", r"\bjoke\b", r"\brecipe\b", r"\bbolo\b", r"\bcake\b",
            r"\bpoema\b", r"\bhist[oó]ria\b", r"\btexto do zero\b", r"\bescreva do zero\b",
            r"\bescrever do zero\b", r"\bcriar do zero\b", r"\bcria do zero\b",
            r"\bconto\b", r"\bpiadas\b", r"\breceitas\b"
        ]
        has_creative_word = any(re.search(pat, q) for pat in creative_keywords)
        
        generation_verbs = [r"\bgere\b", r"\bgerar\b", r"\bcrie\b", r"\bcriar\b", r"\bescreva\b", r"\bescrever\b"]
        has_generation_verb = any(re.search(pat, q) for pat in generation_verbs)
        
        is_reply = bool(re.search(r"\b(respond|respost|reply|re:)\b", q))
        
        if has_creative_word:
            return True
        if has_generation_verb and not is_reply:
            return True
        return False

    async def _generate_creative_body(self, query: str) -> str:
        prompt = (
            f"O utilizador solicitou o seguinte conteúdo para um e-mail:\n"
            f"\"{query}\"\n\n"
            "Gera o corpo do e-mail com base nesse pedido. Devolve apenas o texto puro do e-mail (como receitas, piadas ou textos), "
            "sem saudações redundantes, justificações extras, metadados ou assinaturas fictícias."
        )
        resp = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": "És um assistente de escrita de e-mails criativo. Escreve respostas de alta qualidade em português."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800,
        )
        return (resp.choices[0].message.content or "").strip()

    async def _summarise_relevant(self, query: str, emails: list[dict]) -> str:
        listing = "\n".join(
            f"{i + 1}. De: {e['from']} | Assunto: {e['subject']} | {e['snippet'][:120]}"
            for i, e in enumerate(emails[:10])
        )
        resp = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": "És um assistente de email. Responde em português, de forma clara e concisa.",
                },
                {
                    "role": "user",
                    "content": (
                        f"Pedido: {query}\n\nEmails recentes:\n{listing}\n\n"
                        "Em 2-3 frases: qual é o email mais relevante para este pedido e porquê?"
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=200,
        )
        return resp.choices[0].message.content or "Análise concluída."

    async def _pick_highlight(self, query: str, emails: list[dict]) -> str:
        return await self._summarise_relevant(query, emails)

    async def _generate_draft(self, query: str, context_email: dict) -> str:
        prompt = (
            f"EMAIL RECEBIDO\n"
            f"De: {context_email.get('from', 'Desconhecido')}\n"
            f"Assunto: {context_email.get('subject', 'Sem assunto')}\n"
            f"Conteúdo: {context_email.get('snippet', '')}\n\n"
            f"PEDIDO: {query}\n\n"
            "Gera uma proposta de resposta profissional e concisa em português. "
            "Devolve apenas o texto da resposta pura, sem justificações extras, metadados ou saudações genéricas repetidas."
        )
        resp = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "És um assistente de email profissional. "
                        "Geras respostas diretas e contextualizadas ao email recebido. "
                        "Nunca inclua assinaturas automáticas corporativas ou notas adicionais."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=400,
        )
        return resp.choices[0].message.content or "Não foi possível gerar uma proposta."

    async def _regenerate_body(self, query: str, context_email: dict) -> str:
        prompt = (
            f"EMAIL RECEBIDO\n"
            f"De: {context_email.get('from', 'Desconhecido')}\n"
            f"Assunto: {context_email.get('subject', 'Sem assunto')}\n"
            f"Conteúdo: {context_email.get('snippet', '')}\n\n"
            f"PEDIDO DO UTILIZADOR: {query}\n\n"
            "Com base no email recebido e no pedido do utilizador, gera o corpo do email de resposta sugerido. "
            "Devolve apenas o texto do corpo da mensagem de resposta pura, sem saudações redundantes, sem justificações extras, metadados ou assinaturas fictícias."
        )
        resp = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "És um assistente de email profissional. "
                        "Geras respostas diretas e contextualizadas ao email recebido. "
                        "Nunca inclua assinaturas automáticas corporativas ou notas adicionais."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=400,
        )
        return resp.choices[0].message.content or ""

    def _is_confirmation_query(self, query: str) -> bool:
        q = query.strip().lower()
        if not q:
            return False
        # Se for curta (até 8 palavras)
        if len(q.split()) <= 8:
            return True
        # Se contiver apenas comandos de envio/confirmação com referências ao contexto (como "sobre a receita", "do bolo", etc.)
        # mas sem especificar novos destinatários ou corpos detalhados
        confirmation_patterns = [
            r"\benvie\b", r"\benviar\b", r"\bmande\b", r"\bmandar\b", r"\bdispare\b", 
            r"\bconfirma\b", r"\bconfirmar\b", r"\bmanda\b", r"\bvai\b", r"\benvia\b"
        ]
        has_action = any(re.search(pat, q) for pat in confirmation_patterns)
        if has_action and "@" not in q and len(q) < 45:
            return True
        return False

    async def _extract_from_previous_turn(self, history: List[dict]) -> dict:
        # We need the user's previous message and the assistant's previous message
        # In history (newest to oldest):
        # history[0] is typically the assistant's last message
        # history[1] is typically the user's last message
        prev_assistant = None
        prev_user = None
        for msg in history:
            role = msg.get("role")
            if role == "assistant" and prev_assistant is None:
                prev_assistant = msg.get("content")
            elif role == "user" and prev_user is None:
                prev_user = msg.get("content")
            if prev_assistant is not None and prev_user is not None:
                break
        
        if not prev_assistant and not prev_user:
            return {}

        prompt = f"""PREVIOUS USER QUERY:
{prev_user or "None"}

PREVIOUS ASSISTANT RESPONSE:
{prev_assistant or "None"}
"""
        try:
            resp = await self.client.chat.completions.create(
                model=self.settings.groq_model,
                messages=[
                    {"role": "system", "content": _EXTRACTION_SYSTEM},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=500,
            )
            raw = resp.choices[0].message.content or ""
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            data = json.loads(raw)
            return data
        except Exception as e:
            logger.warning("Failed to extract context from previous turn: %s", e)
            return {}