from groq import AsyncGroq
import json
import re
from typing import Optional, List

from dev_agent.agents.base_agent import BaseAgent
from dev_agent.core.models import AgentType, AgentResult
from dev_agent.core.config import get_settings


class AnimeAgent(BaseAgent):
    """
    Easter egg — activa-se com um botão escondido no frontend.
    Recomenda animes com base no perfil técnico do dev.
    """
    agent_type = AgentType.ANIME

    def __init__(self, user_id: str, user_profile: dict = None):
        self.user_id = user_id
        self.user_profile = user_profile or {}
        self.settings = get_settings()
        self.client = AsyncGroq(api_key=self.settings.groq_api_key)

    async def run(self, query: str, history: Optional[List[dict]] = None) -> AgentResult:
        try:
            recommendation = await self._recommend_anime(query)
            return self.success({"recommendation": recommendation})
        except Exception as e:
            return self.failure(str(e))

    async def _recommend_anime(self, query: str) -> dict:
        """Recomenda anime com base no perfil do dev."""
        profile_text = f"""
        Linguagens: {self.user_profile.get('languages', 'Python')}
        Tipo de projectos: {self.user_profile.get('project_types', 'backend, APIs')}
        Query: {query}
        """
        
        response = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[{
                "role": "system",
                "content": """
                És um agente crítico de anime com profundo conhecimento técnico.
                Recomendas animes baseado no perfil técnico do developer.
                As tuas recomendações têm justificações técnicas e culturais genuínas.
                Responds em português.
                """
            }, {
                "role": "user",
                "content": f"""
                Perfil do dev:
                {profile_text}
                
                Recomenda 3 animes e justifica cada um com base no perfil técnico.
                Responde APENAS com JSON:
                {{
                    "recommendations": [
                        {{
                            "title": "Nome do Anime",
                            "reason": "Porque este dev vai gostar...",
                            "technical_parallel": "É como X em programação porque...",
                            "rating": 9.2
                        }}
                    ]
                }}
                """
            }],
            temperature=0.8,
        )
        
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", content, re.S)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            return {"recommendations": []}

    async def critique_suggestion(self, anime_title: str, user_reason: str) -> dict:
        """
        Critica uma sugestão do utilizador.
        O agente pode concordar ou discordar — e explica porquê.
        """
        response = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[{
                "role": "system",
                "content": "És um crítico de anime honesto e directo. Não tens papas na língua."
            }, {
                "role": "user",
                "content": f"""
                Um developer sugeriu: "{anime_title}"
                Razão dele: "{user_reason}"
                
                Faz uma crítica honesta desta sugestão.
                Diz se concordas ou discordas e porquê.
                Responde somente com o objeto JSON abaixo, sem texto adicional:
                {{
                    "approved": true/false,
                    "critique": "A tua análise crítica...",
                    "score": 7.5,
                    "tags": ["python", "backend"]
                }}
                """
            }],
            temperature=0.9,
        )
        
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = __import__("re").search(r"(\{.*\})", content, __import__("re").S)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    pass
            return {"approved": False, "critique": "Não foi possível analisar.", "score": 0, "tags": []}