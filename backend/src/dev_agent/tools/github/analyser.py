from groq import AsyncGroq
from dev_agent.core.config import get_settings
import json


class GitHubAnalyser:
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncGroq(api_key=self.settings.groq_api_key)

    async def analyse(self, files: list, query: str) -> dict:
        """Usa o Groq para analisar os ficheiros e encontrar problemas."""
        
        files_text = "\n\n".join([
            f"--- {f['path']} ---\n{f['content']}"
            for f in files
        ])
        
        response = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=[{
                "role": "user",
                "content": f"""
                Pedido: {query}
                
                Ficheiros do repositório:
                {files_text}
                
                Analisa o código e responde APENAS com JSON:
                {{
                    "issues": ["problema 1", "problema 2"],
                    "suggestions": ["sugestão 1", "sugestão 2"],
                    "quality_score": 7
                }}
                """
            }],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content
        # Tentar extrair o primeiro bloco JSON se a resposta contiver texto adicional.
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # tentar encontrar o primeiro '{' até o seu correspondente '}' simples
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                maybe = content[start:end+1]
                try:
                    return json.loads(maybe)
                except Exception:
                    pass
            return {"issues": [], "suggestions": ["Análise concluída"], "quality_score": 5}