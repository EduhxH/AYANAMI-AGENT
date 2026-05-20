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
        - "github": para analisar código, repos, criar PRs, ver commits, resumir projetos, inspecionar README, analisar package.json/requirements.txt/pyproject.toml/Dockerfile e trabalhar com repositórios GitHub.
        - "email": para ler emails, responder, enviar, escrever, classificar, gerar propostas de resposta, drafts/rascunhos, sugestões de email e envio de mensagens
        - "anime": apenas se o utilizador pedir recomendações de anime (easter egg)
        
        Usa o agente "github" sempre que o pedido envolver qualquer tipo de análise ou resumo de repositório, README, stars, commits, package.json, requirements.txt, pyproject.toml, Dockerfile, main.py, index.js, app.py ou menção de um repositório específico como "AYANAMI-AGENT".
        
        Usa o agente "email" quando o pedido envolver:
        - Ler, buscar, ou analisar emails
        - Responder a emails (palavras como "responda", "responde", "responder", "reply")
        - Enviar emails (palavras como "envie", "enviar", "mande", "mandar", "envio")
        - Escrever emails, rascunhos ou propostas de resposta (palavras como "escreva", "escrever", "gere uma resposta", "gere uma proposta", "draft", "rascunho", "sugestão", "sugestao")
        - Enviar mensagens ou rascunhos de email (palavras como "envie", "enviar", "mande", "mandar", "envio")
        - Classificar ou organizar emails
        - Qualquer operação de Gmail/correio
        
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
            if any(word in query_lower for word in [
                "repo", "repositório", "repositório", "código", "pr", "github", "commit",
                "resuma", "resumir", "analise", "analisa", "stars", "readme", "dockerfile",
                "package.json", "requirements.txt", "pyproject.toml", "main.py", "index.js", "app.py",
            ]):
                agents.append(AgentType.GITHUB)
            if any(word in query_lower for word in [
                "email", "gmail", "mensagem", "responde", "responder", "envie", "enviar", 
                "mande", "mandar", "escreva", "escrever", "gere uma resposta", "gere uma proposta",
                "resposta", "envio", "compose", "rascunho", "draft", "correio", "sugestão", "sugestao"
            ]):
                agents.append(AgentType.EMAIL)
            
            result_agents = agents or [AgentType.GITHUB]
            print(f"[PLANNER] === INTENÇÃO DETECTADA (FALLBACK) ===")
            print(f"[PLANNER] Agentes selecionados: {[a.value for a in result_agents]}")
            print("=" * 80)
            return result_agents  