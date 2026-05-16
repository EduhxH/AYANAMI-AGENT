from typing import Callable, Awaitable, Optional

from groq import AsyncGroq

from dev_agent.agents.base_agent import BaseAgent
from dev_agent.core.config import get_settings
from dev_agent.core.models import AgentType, AgentResult
from dev_agent.tools.email.reader import GmailReader

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

        try:
            reader = GmailReader(self.token, on_token_refresh=self.on_token_refresh)
            emails = await reader.get_recent_emails(max_results=15)

            if not emails:
                return self.success(
                    {
                        "emails_found": 0,
                        "emails": [],
                        "highlight": "Não há emails recentes na inbox.",
                    }
                )

            highlight = await self._pick_highlight(query, emails)

            return self.success(
                {
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
