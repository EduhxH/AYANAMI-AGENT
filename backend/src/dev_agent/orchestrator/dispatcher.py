import asyncio
from typing import List, Dict, Any, Callable, Awaitable, Optional

from dev_agent.core.models import AgentType, AgentResult
from dev_agent.agents.github_agent import GitHubAgent
from dev_agent.agents.email_agent import EmailAgent
from dev_agent.agents.anime_agent import AnimeAgent

TokenRefreshCallback = Callable[[], Awaitable[str]]


class Dispatcher:
    def __init__(
        self,
        user_data: Dict[str, Any],
        on_google_token_refresh: Optional[TokenRefreshCallback] = None,
    ):
        self.user_data = user_data
        self.on_google_token_refresh = on_google_token_refresh

    async def run(self, query: str, agents: List[AgentType], history: Optional[List[dict]] = None) -> List[AgentResult]:
        print(f"[DISPATCHER] run() chamado com {len(agents)} agentes")
        print(f"[DISPATCHER] Query: {query!r}")
        print(f"[DISPATCHER] user_data keys: {list(self.user_data.keys())}")
        # Detecção rápida se a query menciona GitHub / repositórios
        q_low = (query or "").lower()
        github_mentioned = "github" in q_low or "reposit" in q_low

        agent_results: List[AgentResult] = []

        # Se for um caso GitHub+Email, execute o GitHub primeiro e injete o resultado no EmailAgent
        if github_mentioned and AgentType.GITHUB in agents and AgentType.EMAIL in agents:
            print("[DISPATCHER] Fluxo especial: GitHub mencionado — executando GitHubAgent primeiro")
            gh_agent = self._get_agent(AgentType.GITHUB)
            if gh_agent:
                gh_result = await gh_agent.run(query, history=history)
                agent_results.append(gh_result)
                # Prepare EmailAgent com contexto do GitHub
                email_agent = self._get_agent(AgentType.EMAIL)
                if email_agent:
                    # Tentativa robusta de anexar o payload do GitHub como contexto
                    try:
                        repos = gh_result.data.get("repositories") if gh_result and gh_result.success else None
                    except Exception:
                        repos = None
                    setattr(email_agent, "github_repositories", repos)

                    # Disparar EmailAgent (junto com os restantes agentes) em paralelo
                    tasks = []
                    active_agents = []
                    for agent_type in agents:
                        if agent_type == AgentType.GITHUB:
                            continue
                        print(f"[DISPATCHER] Criando agente: {agent_type.value}")
                        agent = self._get_agent(agent_type) if agent_type != AgentType.EMAIL else email_agent
                        if agent:
                            print(f"[DISPATCHER] Agente {agent_type.value} criado com sucesso")
                            tasks.append(agent.run(query, history=history))
                            active_agents.append(agent_type)
                        else:
                            print(f"[DISPATCHER] FALHA: Agente {agent_type.value} retornou None")

                    print(f"[DISPATCHER] Executando {len(tasks)} tarefas em paralelo...")
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for agent_type, result in zip(active_agents, results):
                        if isinstance(result, Exception):
                            print(f"[DISPATCHER] Agente {agent_type.value} retornou Exception: {result}")
                            agent_results.append(
                                AgentResult(agent=agent_type, success=False, data={}, error=str(result))
                            )
                        else:
                            print(f"[DISPATCHER] Agente {agent_type.value} retornou AgentResult: success={result.success}")
                            agent_results.append(result)

                    return agent_results

        # Fluxo padrão: executar todos os agentes em paralelo
        tasks = []
        active_agents = []
        for agent_type in agents:
            print(f"[DISPATCHER] Criando agente: {agent_type.value}")
            agent = self._get_agent(agent_type)
            if agent:
                print(f"[DISPATCHER] Agente {agent_type.value} criado com sucesso")
                tasks.append(agent.run(query, history=history))
                active_agents.append(agent_type)
            else:
                print(f"[DISPATCHER] FALHA: Agente {agent_type.value} retornou None")

        print(f"[DISPATCHER] Executando {len(tasks)} tarefas em paralelo...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for agent_type, result in zip(active_agents, results):
            if isinstance(result, Exception):
                print(f"[DISPATCHER] Agente {agent_type.value} retornou Exception: {result}")
                agent_results.append(
                    AgentResult(
                        agent=agent_type,
                        success=False,
                        data={},
                        error=str(result),
                    )
                )
            else:
                print(f"[DISPATCHER] Agente {agent_type.value} retornou AgentResult: success={result.success}")
                agent_results.append(result)

        return agent_results

    def _get_agent(self, agent_type: AgentType):
        if agent_type == AgentType.GITHUB:
            token = self.user_data.get("github_token")
            username = self.user_data.get("github_username")
            print(f"[DISPATCHER] _get_agent(GITHUB):")
            print(f"  - token: {'***' if token else 'NULL/EMPTY'}")
            print(f"  - github_username: {username}")
            return GitHubAgent(
                token=token,
                github_username=username,
            )
        if agent_type == AgentType.EMAIL:
            token = self.user_data.get("google_token")
            print(f"[DISPATCHER] _get_agent(EMAIL):")
            print(f"  - token: {'***' if token else 'NULL/EMPTY'}")
            return EmailAgent(
                token=token,
                on_token_refresh=self.on_google_token_refresh,
            )
        if agent_type == AgentType.ANIME:
            user_id = self.user_data.get("user_id")
            print(f"[DISPATCHER] _get_agent(ANIME):")
            print(f"  - user_id: {user_id}")
            return AnimeAgent(user_id=user_id)
        return None
