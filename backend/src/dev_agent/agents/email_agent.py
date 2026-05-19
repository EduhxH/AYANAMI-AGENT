"""
EmailAgent — refactored & calibrated.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Awaitable, Callable, Literal, Optional

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
        # Sanitização simples por regex nativa para evitar dependências externas estritas
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
- "draft" → The user wants to compose, write, suggest, or generate a response text, proposal, or draft (e.g., "gere uma proposta", "escreva uma resposta", "sugira um texto", "crie um rascunho"). Even if a recipient email is present in the prompt, if the action verbs are about "generating/suggesting/writing/proposing", it is ALWAYS a "draft", NOT a "send".
- "read"  → The user wants to read, view, list, search, or analyse their inbox.

Crucial Instruction:
If the user uses words like "proposta", "sugestão", "rascunho", "draft", "escreva uma resposta" or "como responder", the intent is STRICTLY "draft". Do NOT classify as "send" unless the user gives a direct command to dispatch the message immediately.

Respond with ONLY the JSON object — no markdown, no extra text.
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
    ) -> None:
        self.token = token
        self.on_token_refresh = on_token_refresh
        self.settings = get_settings()
        self.client = AsyncGroq(api_key=self.settings.groq_api_key)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    async def run(self, query: str) -> AgentResult:
        if not self.token:
            return self.failure("Gmail não está ligado. Liga a tua conta primeiro.")

        intent = await self._classify(query)
        if intent is None:
            return self.failure("Não consegui interpretar o pedido. Tenta ser mais específico.")

        logger.debug("EmailAgent intent=%s reasoning=%s", intent.intent, intent.reasoning)

        match intent.intent:
            case "send":
                return await self._handle_send(intent)
            case "draft":
                return await self._handle_draft(query, intent)
            case "read":
                return await self._handle_read(query)

    # ------------------------------------------------------------------
    # Intent classification (single LLM call)
    # ------------------------------------------------------------------

    async def _classify(self, query: str) -> Optional[EmailIntent]:
        for attempt in range(2):
            try:
                resp = await self.client.chat.completions.create(
                    model=self.settings.groq_model,
                    messages=[
                        {"role": "system", "content": _CLASSIFY_SYSTEM},
                        {"role": "user", "content": query},
                    ],
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

    async def _handle_send(self, intent: EmailIntent) -> AgentResult:
        if not intent.recipient:
            return self.failure(
                "Não consegui identificar o destinatário. "
                "Inclui o endereço de email no pedido (ex: 'Envia para user@example.com: ...')."
            )
        body = (intent.body or "").strip()
        if len(body) < 3:
            return self.failure(
                "Corpo do email muito curto ou vazio. "
                "Fornece o texto que queres enviar."
            )

        try:
            sender = GmailSender(self.token, on_token_refresh=self.on_token_refresh)
            result = await sender.send_email(
                to=intent.recipient,
                subject=intent.subject or "Sem assunto",
                body=body,
            )
            return self.success({
                "action": "send",
                "recipient": intent.recipient,
                "subject": intent.subject,
                "body_preview": body[:150],
                "result": result,
            })
        except Exception as exc:
            logger.exception("Erro ao enviar email")
            return self.failure(f"Erro ao enviar email: {exc}")

    async def _handle_draft(self, query: str, intent: EmailIntent) -> AgentResult:
        if intent.body and len(intent.body.strip()) > 30 and "prop" not in intent.body.lower():
            return self.success({
                "action": "draft",
                "proposed_response": intent.body.strip(),
                "instructions": (
                    "Sugestão gerada. Usa 'Envia para user@example.com: [texto]' para enviar."
                ),
            })

        try:
            reader = GmailReader(self.token, on_token_refresh=self.on_token_refresh)
            emails = await reader.get_recent_emails(max_results=15)
        except Exception as exc:
            logger.exception("Erro ao ler emails para draft")
            return self.failure(f"Erro ao aceder ao Gmail: {exc}")

        if not emails:
            return self.failure("Não há emails recentes para usar como contexto.")

        context_email = self._pick_most_relevant(query, emails)
        draft_text = await self._generate_draft(query, context_email)

        return self.success({
            "action": "draft",
            "context_from": context_email.get("from", "Desconhecido"),
            "context_subject": context_email.get("subject", "Sem assunto"),
            "proposed_response": draft_text,
            "instructions": (
                "Sugestão de resposta. Usa 'Envia para user@example.com: [texto]' para enviar."
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

    async def _generate_draft(self, query: str, context_email: dict) -> str:
        prompt = (
            f"EMAIL RECEBIDO\n"
            f"De: {context_email.get('from', 'Desconhecido')}\n"
            f"Assunto: {context_email.get('subject', 'Sem assunto')}\n"
            f"Conteúdo: {context_email.get('snippet', '')}\n\n"
            f"PEDIDO: {query}\n\n"
            "Gera uma proposta de resposta professional e concisa em português. "
            "Devolve apenas o texto da resposta, sem explicações."
        )
        resp = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "És um assistente de email profissional. "
                        "Geras respostas directas, claras e educadas."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=400,
        )
        return resp.choices[0].message.content or "Não foi possível gerar uma proposta."