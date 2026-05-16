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

    async def run(self, query: str, agents: List[AgentType]) -> List[AgentResult]:
        tasks = []
        active_agents = []
        for agent_type in agents:
            agent = self._get_agent(agent_type)
            if agent:
                tasks.append(agent.run(query))
                active_agents.append(agent_type)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        agent_results = []
        for agent_type, result in zip(active_agents, results):
            if isinstance(result, Exception):
                agent_results.append(
                    AgentResult(
                        agent=agent_type,
                        success=False,
                        data={},
                        error=str(result),
                    )
                )
            else:
                agent_results.append(result)

        return agent_results

    def _get_agent(self, agent_type: AgentType):
        if agent_type == AgentType.GITHUB:
            return GitHubAgent(
                token=self.user_data.get("github_token"),
                github_username=self.user_data.get("github_username"),
            )
        if agent_type == AgentType.EMAIL:
            return EmailAgent(
                token=self.user_data.get("google_token"),
                on_token_refresh=self.on_google_token_refresh,
            )
        if agent_type == AgentType.ANIME:
            return AnimeAgent(user_id=self.user_data.get("user_id"))
        return None
