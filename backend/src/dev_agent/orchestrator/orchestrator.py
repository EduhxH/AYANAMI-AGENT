import json

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
        print(f"[ORCHESTRATOR] Recebendo TaskRequest: query={request.query!r}, agents={request.agents}")
        print(f"[ORCHESTRATOR] user_data: user_id={user_data.get('user_id')}, github_token={'***' if user_data.get('github_token') else 'NULL'}, github_username={user_data.get('github_username')}")
        
        agents = request.agents or await self.planner.decide_agents(request.query)
        print(f"[ORCHESTRATOR] Agentes a executar: {[a.value for a in agents]}")

        dispatcher = Dispatcher(user_data, self.on_google_token_refresh)
        print(f"[ORCHESTRATOR] Iniciando Dispatcher com {len(agents)} agentes...")
        
        results = await dispatcher.run(request.query, agents)
        print(f"[ORCHESTRATOR] Dispatcher completado com {len(results)} resultados")

        summary = await self._generate_summary(request.query, results)
        print(f"[ORCHESTRATOR] Summary gerado: {summary[:100]}...")

        return OrchestratorResult(
            query=request.query,
            results=results,
            summary=summary,
        )

    async def _generate_summary(self, query: str, results: List[AgentResult]) -> str:
        lines = []
        for r in results:
            if r.success:
                agent_text = self._format_agent_success(r)
                lines.append(agent_text)
            else:
                lines.append(f"Agente {r.agent}: Erro — {r.error or r.data}")

        results_text = "\n\n".join(lines)

        response = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[
                {
                    "role": "user",
                    "content": f"""
Pedido do utilizador: "{query}"

Resultados dos agentes:
{results_text}

Baseia a resposta final nestes resultados, especialmente no contexto do repositório fornecido.
Escreve em português, de forma directa, técnica e sem especulações.
""",
                }
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content

    def _format_agent_success(self, result: AgentResult) -> str:
        data = result.data or {}
        if data.get("repo_context_text"):
            return f"Agente {result.agent}: Sucesso — Contexto do repositório:\n{data['repo_context_text']}"
        return f"Agente {result.agent}: Sucesso — {json.dumps(data, ensure_ascii=False, indent=2)}"
