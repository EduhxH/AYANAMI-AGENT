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
        print("=" * 80)
        print("[PLANNER] === INPUT DO CHAT ===")
        print(f"[PLANNER] Query recebida: {query!r}")
        print("=" * 80)
        
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
        print(f"[PLANNER] Resposta do LLM (raw): {content!r}")
        
        try:
            data = json.loads(content)
            agents = [AgentType(a) for a in data["agents"]]
            print(f"[PLANNER] === INTENÇÃO DETECTADA ===")
            print(f"[PLANNER] Agentes selecionados: {[a.value for a in agents]}")
            print("=" * 80)
            return agents
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"[PLANNER] ERRO ao parsear JSON LLM: {e}")
            print(f"[PLANNER] Caindo para heurística de fallback...")
            
            agents = []
            query_lower = query.lower()
            if any(word in query_lower for word in ["repo", "código", "pr", "github", "commit", "crie", "criar", "delete", "deletar", "remover"]):
                agents.append(AgentType.GITHUB)
            if any(word in query_lower for word in ["email", "gmail", "mensagem", "responde"]):
                agents.append(AgentType.EMAIL)
            
            result_agents = agents or [AgentType.GITHUB]
            print(f"[PLANNER] === INTENÇÃO DETECTADA (FALLBACK) ===")
            print(f"[PLANNER] Agentes selecionados: {[a.value for a in result_agents]}")
            print("=" * 80)
            return result_agents  