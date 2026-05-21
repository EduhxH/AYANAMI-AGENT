import asyncio
import traceback
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

        agent_results: List[AgentResult] = []

        # GitHub must complete before Email when both are requested
        if AgentType.GITHUB in agents and AgentType.EMAIL in agents:
            print("[DISPATCHER] Dependência GitHub→Email: executando GitHubAgent primeiro")
            gh_agent = self._get_agent(AgentType.GITHUB)
            if gh_agent:
                gh_result = await gh_agent.run(query, history=history)
                agent_results.append(gh_result)

                if not gh_result.success:
                    gh_error = gh_result.error or gh_result.message or "operação GitHub falhou"
                    print(f"[DISPATCHER] GitHubAgent falhou — email não será executado: {gh_error}")
                    agent_results.append(
                        AgentResult(
                            agent=AgentType.EMAIL,
                            success=False,
                            data={},
                            error=f"Não foi possível enviar o email porque a operação GitHub falhou: {gh_error}",
                            message=f"Não foi possível enviar o email: {gh_error}",
                        )
                    )
                    remaining = [a for a in agents if a not in (AgentType.GITHUB, AgentType.EMAIL)]
                    if remaining:
                        agent_results.extend(
                            await self._run_agents_parallel(query, remaining, history=history)
                        )
                    return agent_results

                email_agent = self._get_agent(AgentType.EMAIL)
                if email_agent:
                    self._inject_github_context(email_agent, gh_result)

                remaining = [a for a in agents if a != AgentType.GITHUB]
                if remaining:
                    email_agent_override = email_agent if email_agent else None
                    agent_results.extend(
                        await self._run_agents_parallel(
                            query,
                            remaining,
                            history=history,
                            email_agent_override=email_agent_override,
                        )
                    )
                return agent_results

        return await self._run_agents_parallel(query, agents, history=history)

    async def _run_agents_parallel(
        self,
        query: str,
        agents: List[AgentType],
        history: Optional[List[dict]] = None,
        email_agent_override: Optional[EmailAgent] = None,
    ) -> List[AgentResult]:
        agent_results: List[AgentResult] = []
        tasks = []
        active_agents = []

        for agent_type in agents:
            print(f"[DISPATCHER] Criando agente: {agent_type.value}")
            if agent_type == AgentType.EMAIL and email_agent_override is not None:
                agent = email_agent_override
            else:
                agent = self._get_agent(agent_type)
            if agent:
                print(f"[DISPATCHER] Agente {agent_type.value} criado com sucesso")
                tasks.append(agent.run(query, history=history))
                active_agents.append(agent_type)
            else:
                print(f"[DISPATCHER] FALHA: Agente {agent_type.value} retornou None")

        if not tasks:
            return agent_results

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
                        message=str(result),
                        errors=[
                            "".join(
                                traceback.format_exception(
                                    type(result), result, result.__traceback__
                                )
                            )
                        ],
                    )
                )
            else:
                print(f"[DISPATCHER] Agente {agent_type.value} retornou AgentResult: success={result.success}")
                agent_results.append(result)

        return agent_results

    def _inject_github_context(self, email_agent: EmailAgent, gh_result: AgentResult) -> None:
        repos = gh_result.data.get("repositories") if gh_result.data else None
        if repos:
            email_agent.github_repositories = repos

        summary_parts: List[str] = []
        if gh_result.data.get("repo_context_text"):
            summary_parts.append(gh_result.data["repo_context_text"])
        if gh_result.data.get("message"):
            summary_parts.append(gh_result.data["message"])
        if repos and not gh_result.data.get("repo_context_text"):
            summary_parts.append("\n".join(f"- {r}" for r in repos))

        if summary_parts:
            email_agent.github_summary = "\n\n".join(summary_parts)

        print(
            f"[DISPATCHER] Contexto GitHub injetado no EmailAgent: "
            f"repos={len(repos) if repos else 0}, summary={'sim' if email_agent.github_summary else 'não'}"
        )

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
