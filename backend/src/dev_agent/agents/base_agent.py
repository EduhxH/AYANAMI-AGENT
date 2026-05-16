from abc import ABC, abstractmethod
from dev_agent.core.models import AgentResult, AgentType


class BaseAgent(ABC):
    """Todos os agentes herdam desta classe base."""
    
    agent_type: AgentType  
    
    @abstractmethod
    async def run(self, query: str) -> AgentResult:
        """Executa o agente e devolve um resultado."""
        pass
    
    def success(self, data: dict) -> AgentResult:
        return AgentResult(agent=self.agent_type, success=True, data=data)
    
    def failure(self, error: str) -> AgentResult:
        return AgentResult(agent=self.agent_type, success=False, data={}, error=error)