from groq import AsyncGroq
from typing import Optional, List, Callable, Awaitable

from dev_agent.core.config import get_settings
from dev_agent.core.models import TaskRequest, OrchestratorResult, AgentType, AgentResult
from dev_agent.orchestrator.planner import Planner
from dev_agent.orchestrator.dispatcher import Dispatcher

TokenRefreshCallback = Callable[[], Awaitable[str]]


class Orchestrator:
    def __init__(self, on_google_token_refresh: Optional[TokenRefreshCallback] = None):
        self.settings = get_settings()
        self.client = AsyncGroq(api_key=self.settings.groq_api_key)
        self.planner = Planner()
        self.on_google_token_refresh = on_google_token_refresh

    async def handle(self, request: TaskRequest, user_data: dict) -> OrchestratorResult:
        agents = request.agents or await self.planner.decide_agents(request.query)

        dispatcher = Dispatcher(user_data, self.on_google_token_refresh)
        results = await dispatcher.run(request.query, agents)

        summary = await self._generate_summary(request.query, results)

        return OrchestratorResult(
            query=request.query,
            results=results,
            summary=summary,
        )

    async def _generate_summary(self, query: str, results: List[AgentResult]) -> str:
        lines = []
        for r in results:
            if r.success:
                lines.append(f"Agente {r.agent}: Sucesso — {r.data}")
            else:
                lines.append(f"Agente {r.agent}: Erro — {r.error or r.data}")

        results_text = "\n".join(lines)

        response = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
Pedido do utilizador: "{query}"

Resultados dos agentes:
{results_text}

Cria uma resposta clara e útil para o utilizador com base nestes resultados.
Escreve em português, de forma directa e técnica.
Se houve erros, explica o que o utilizador deve fazer (ex: religar conta, activar API).
""",
                }
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content
