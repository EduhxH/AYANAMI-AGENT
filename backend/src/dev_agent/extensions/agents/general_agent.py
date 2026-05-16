"""

Agente de conversa geral — pesquisa ao vivo via Groq Compound (GROQ_API_KEY).

"""



import re



from groq import AsyncGroq



from dev_agent.agents.base_agent import BaseAgent

from dev_agent.core.config import get_settings

from dev_agent.core.models import AgentType, AgentResult

from dev_agent.extensions.tools.groq_live_search import (
    answer_with_live_search,
    infer_search_country,
    is_payload_too_large,
    pick_search_model,
)

from dev_agent.extensions.tools.web_search import (

    format_search_results,

    legacy_search_configured,

    search_web,

)

from dev_agent.preferences.context import with_system_preamble



_SEARCH_HINTS = (

    "search",

    "pesquisa",

    "pesquisar",

    "procura",

    "google",

    "what is",

    "what are",

    "who is",

    "how does",

    "how do",

    "latest",

    "news",

    "notícias",

    "noticias",

    "current",

    "atual",

    "hoje",

    "agora",

    "ultima hora",

    "última hora",

    "breaking",

    "ao vivo",

    "em tempo real",

    "o que é",

    "o que e",

    "quem é",

    "quem e",

    "como funciona",

    "explain",

    "explica",

    "tutorial",

)





class GeneralConversationAgent(BaseAgent):

    agent_type = AgentType.GENERAL



    def __init__(self):

        self.settings = get_settings()

        self.client = AsyncGroq(api_key=self.settings.groq_api_key)



    async def run(self, query: str) -> AgentResult:

        try:

            language_hint = self._detect_language_hint(query)



            if self._should_search(query):

                return await self._answer_with_search(query, language_hint)



            return await self._answer_without_search(query, language_hint)

        except Exception as e:

            return self.failure(str(e))



    async def _answer_with_search(
        self, query: str, language_hint: str
    ) -> AgentResult:
        country = infer_search_country(query, self.settings.groq_search_country)
        model = pick_search_model(
            query,
            default_model=self.settings.groq_search_model,
            live_model=self.settings.groq_search_model_live,
        )

        answer = ""
        used_search = False
        try:
            answer, used_search = await answer_with_live_search(
                self.client,
                query,
                model=model,
                country=country,
                language_hint=language_hint,
                mini_fallback_model=self.settings.groq_search_model,
            )
        except Exception as exc:
            if not is_payload_too_large(exc) and not legacy_search_configured():
                return self.failure(str(exc))

        if answer:
            return self.success(
                {"answer": answer, "used_web_search": used_search}
            )

        if legacy_search_configured():
            try:
                hits = await search_web(query, max_results=3)
                search_block = format_search_results(hits)
                if search_block:
                    return await self._synthesize_with_context(
                        query, language_hint, search_block, used_search=True
                    )
            except Exception as exc:
                return self.failure(str(exc))

        return self.failure(
            "Não foi possível obter resultados de pesquisa. "
            "Tenta uma pergunta mais específica ou configura TAVILY_API_KEY como fallback."
        )



    async def _answer_without_search(

        self, query: str, language_hint: str

    ) -> AgentResult:

        user_content = f"""User message:

{query}



Reply in the same language as the user ({language_hint}).

Keep the answer short and direct unless the user asks for detail."""



        messages = with_system_preamble(

            [{"role": "user", "content": user_content}]

        )



        response = await self.client.chat.completions.create(

            model=self.settings.groq_model,

            messages=messages,

            temperature=0.6,

        )



        answer = (response.choices[0].message.content or "").strip()

        if not answer:

            return self.failure("Empty response from the model.")



        return self.success({"answer": answer, "used_web_search": False})



    async def _synthesize_with_context(

        self,

        query: str,

        language_hint: str,

        search_block: str,

        *,

        used_search: bool,

    ) -> AgentResult:

        user_content = f"""User message:

{query}



Web search results:

{search_block}



Reply in the same language as the user ({language_hint}).

Use search results when provided. Keep the answer short and direct."""



        messages = with_system_preamble(

            [{"role": "user", "content": user_content}]

        )



        response = await self.client.chat.completions.create(

            model=self.settings.groq_model,

            messages=messages,

            temperature=0.6,

        )



        answer = (response.choices[0].message.content or "").strip()

        if not answer:

            return self.failure("Empty response from the model.")



        return self.success({"answer": answer, "used_web_search": used_search})



    def _should_search(self, query: str) -> bool:

        q = query.lower()

        if any(hint in q for hint in _SEARCH_HINTS):

            return True

        if re.search(r"\b20\d{2}\b", q):

            return True

        if "?" in query and len(query.split()) >= 3:

            return True

        return False



    def _detect_language_hint(self, query: str) -> str:

        lower = query.lower()

        pt_markers = (

            "olá",

            "ola",

            "como",

            "estás",

            "estas",

            "obrigado",

            "porque",

            "não",

            "nao",

            "é",

            "ção",

            "ções",

            "ã",

            "õ",

        )

        if any(m in lower for m in pt_markers):

            return "Portuguese"

        return "the user's language"


