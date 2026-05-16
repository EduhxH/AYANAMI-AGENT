from groq import AsyncGroq
from dev_agent.core.config import get_settings
from dev_agent.core.models import AgentType
from typing import List
import json


class Planner:
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncGroq(api_key=self.settings.groq_api_key)

    async def decide_agents(self, query: str) -> List[AgentType]:
        """
        Usa o LLM para analisar a query e decidir quais agentes activar.
        Devolve uma lista de AgentType.
        """
        prompt = f"""
        Analisa o seguinte pedido de um developer e decide quais agentes activar.
        
        Pedido: "{query}"
        
        Agentes disponíveis:
        - "github": para analisar código, repos, criar PRs, ver commits
        - "email": para ler emails, responder, classificar
        - "anime": apenas se o utilizador pedir recomendações de anime (easter egg)
        
        Responde APENAS com JSON válido, sem texto adicional:
        {{"agents": ["github", "email"]}}
        
        Usa apenas os agentes necessários para o pedido.
        """
        
        response = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  
        )
        
        content = response.choices[0].message.content.strip()
        
        try:
            data = json.loads(content)
            return [AgentType(a) for a in data["agents"]]
        except (json.JSONDecodeError, KeyError, ValueError):
           
            agents = []
            query_lower = query.lower()
            if any(word in query_lower for word in ["repo", "código", "pr", "github", "commit"]):
                agents.append(AgentType.GITHUB)
            if any(word in query_lower for word in ["email", "gmail", "mensagem", "responde"]):
                agents.append(AgentType.EMAIL)
            return agents or [AgentType.GITHUB]  