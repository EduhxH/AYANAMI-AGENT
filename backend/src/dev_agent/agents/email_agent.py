from typing import Callable, Awaitable, Optional
import re

from groq import AsyncGroq

from dev_agent.agents.base_agent import BaseAgent
from dev_agent.core.config import get_settings
from dev_agent.core.models import AgentType, AgentResult
from dev_agent.tools.email.reader import GmailReader
from dev_agent.tools.email.sender import GmailSender

TokenRefreshCallback = Callable[[], Awaitable[str]]


class EmailAgent(BaseAgent):
    agent_type = AgentType.EMAIL

    def __init__(
        self,
        token: str | None,
        on_token_refresh: Optional[TokenRefreshCallback] = None,
    ):
        self.token = token
        self.on_token_refresh = on_token_refresh
        self.settings = get_settings()
        self.client = AsyncGroq(api_key=self.settings.groq_api_key)

    async def run(self, query: str) -> AgentResult:
        if not self.token:
            return self.failure("Gmail não está ligado. Liga a tua conta primeiro.")

        # Detectar intenção: ler ou enviar?
        is_send_intent = self._is_send_intent(query)

        if is_send_intent:
            # Extrair destinatário e corpo do email
            recipient, subject, body = await self._extract_email_details(query)
            if not recipient:
                return self.failure("Não consegui extrair o destinatário. Tenta: 'Enviar para user@example.com: Olá...'")
            
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
            except Exception as e:
                return self.failure(f"Erro ao enviar email: {str(e)}")
        else:
            # Ação padrão: ler e analisar emails
            try:
                reader = GmailReader(self.token, on_token_refresh=self.on_token_refresh)
                emails = await reader.get_recent_emails(max_results=15)

                if not emails:
                    return self.success(
                        {
                            "action": "read",
                            "emails_found": 0,
                            "emails": [],
                            "highlight": "Não há emails recentes na inbox.",
                        }
                    )

                highlight = await self._pick_highlight(query, emails)

                return self.success(
                    {
                        "action": "read",
                        "emails_found": len(emails),
                        "emails": emails[:10],
                        "highlight": highlight,
                    }
                )
            except Exception as e:
                return self.failure(str(e))

    async def _pick_highlight(self, query: str, emails: list) -> str:
        """Escolhe o email mais relevante para o pedido do utilizador."""
        listing = "\n".join(
            [
                f"{i + 1}. De: {e['from']} | Assunto: {e['subject']} | {e['snippet'][:120]}"
                for i, e in enumerate(emails[:10])
            ]
        )

        response = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "És um assistente de email. Responde em português, de forma clara e útil."
                    ),
                },
                {
                    "role": "user",
                    "content": f"""
Pedido: {query}

Emails recentes:
{listing}

Indica qual é o email mais interessante/relevante para este pedido e explica porquê em 2-4 frases.
Se nenhum for especialmente relevante, diz qual merece atenção primeiro.
""",
                },
            ],
            temperature=0.5,
        )

        return response.choices[0].message.content or "Análise concluída."

    def _is_send_intent(self, query: str) -> bool:
        """Detecta se a query é uma intenção de ENVIO de email."""
        query_lower = query.lower()
        
        # Palavras-chave explícitas de envio
        send_keywords = [
            "envie",
            "enviar",
            "mande",
            "mandar",
            "responda",
            "responder",
            "escreva",
            "escrever",
            "compose",
            "envio",
            "gere uma proposta",
            "gere uma resposta",
        ]
        
        # Verificar se contém palavras-chave de envio
        for keyword in send_keywords:
            if keyword in query_lower:
                return True
        
        # Detectar padrão de texto longo entre aspas (possível corpo de email)
        # Exemplo: 'Enviar para user@example.com: "Este é o corpo do email"'
        if '"' in query and len(query) > 50:
            return True
        
        if "'" in query and len(query) > 50:
            return True
        
        return False

    async def _extract_email_details(self, query: str) -> tuple:
        """
        Extrai destinatário, assunto e corpo da query.
        Retorna (destinatário, assunto, corpo) ou (None, "", "") se falhar.
        """
        # Tentar extrair email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_match = re.search(email_pattern, query)
        recipient = email_match.group(0) if email_match else None
        
        if not recipient:
            return None, "", ""
        
        # Tentar extrair corpo entre aspas
        body = ""
        quote_pattern = r'["\']([^"\']+)["\']'
        quote_match = re.search(quote_pattern, query)
        if quote_match:
            body = quote_match.group(1)
        else:
            # Se não houver aspas, usar o resto da query após o email
            parts = query.split(recipient, 1)
            if len(parts) > 1:
                body = parts[1].strip().lstrip(":").strip()
        
        # Extrair assunto (pode estar após "para:" ou "assunto:")
        subject = "Resposta"
        subject_pattern = r'(?:assunto|subject|subj)\s*[:=]\s*([^\n]+)'
        subject_match = re.search(subject_pattern, query, re.IGNORECASE)
        if subject_match:
            subject = subject_match.group(1).strip()
        elif "resposta" in query.lower() or "responda" in query.lower():
            subject = "Re: " + (subject if subject else "Mensagem")
        
        # Se o corpo ainda estiver vazio, usar a query completa após o email
        if not body:
            body = query.replace(recipient, "").strip()
            body = re.sub(r'^[:\-\s]+', '', body).strip()
        
        return recipient, subject, body

