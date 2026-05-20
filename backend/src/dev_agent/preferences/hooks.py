"""
Extensões do orchestrator e agentes LLM — injeta preferências sem alterar ficheiros existentes.
"""

from typing import List

from dev_agent.core.models import AgentResult
from dev_agent.database.connection import get_database
from dev_agent.database.repositories.user_preferences import UserPreferencesRepository
from dev_agent.preferences.context import set_preamble, with_system_preamble
from dev_agent.preferences.prompt import build_agent_system_preamble


def install_orchestrator_hooks() -> None:
    from dev_agent.orchestrator.orchestrator import Orchestrator

    if getattr(Orchestrator, "_preferences_hooks_installed", False):
        return

    _original_handle = Orchestrator.handle
    _original_generate_summary = Orchestrator._generate_summary

    async def handle_with_preferences(self, request, user_data, history=None):
        db = get_database()
        from dev_agent.database.repositories.users import UsersRepository

        user = await UsersRepository(db).find_by_id(user_data["user_id"])
        default_name = user.email.split("@")[0] if user else "Developer"

        prefs_repo = UserPreferencesRepository(db)
        prefs = await prefs_repo.get_or_create(
            user_data["user_id"],
            default_display_name=default_name,
        )

        github_username = user_data.get("github_username")
        github_connected = bool(user_data.get("github_token"))
        google_connected = bool(user_data.get("google_token"))

        account_context = (
            f"GitHub connected: {github_connected}. "
            f"GitHub username: {github_username or 'not provided'}. "
            f"Google connected: {google_connected}."
        )

        preamble = build_agent_system_preamble(prefs, account_context=account_context)
        set_preamble(preamble)
        self._ayanami_system_preamble = preamble
        return await _original_handle(self, request, user_data, history=history)

    async def generate_summary_with_preferences(
        self, query: str, results: List[AgentResult], history=None
    ) -> str:
        lines = []
        for r in results:
            if r.success:
                lines.append(f"Agente {r.agent}: Sucesso — {r.data}")
            else:
                lines.append(f"Agente {r.agent}: Erro — {r.error or r.data}")

        results_text = "\n".join(lines)

        messages = []
        if history:
            for msg in reversed(history):
                messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content")
                })

        messages.append({
            "role": "user",
            "content": f"""
Pedido do utilizador: "{query}"

Resultados dos agentes:
{results_text}

Cria uma resposta clara e útil para o utilizador com base nestes resultados.
Escreve em português, de forma directa e técnica.
Se houve erros, explica o que o utilizador deve fazer (ex: religar conta, activar API).
""",
        })

        messages = with_system_preamble(messages)

        response = await self.client.chat.completions.create(
            model=self.settings.groq_model,
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content

    Orchestrator.handle = handle_with_preferences
    Orchestrator._generate_summary = generate_summary_with_preferences
    Orchestrator._preferences_hooks_installed = True

    _install_agent_llm_hooks()


_llm_hooks_installed = False


def _install_agent_llm_hooks() -> None:
    """Injecta preamble nas outras chamadas Groq (analyser, email, anime, planner)."""
    global _llm_hooks_installed
    if _llm_hooks_installed:
        return

    from dev_agent.tools.github.analyser import GitHubAnalyser
    from dev_agent.agents.email_agent import EmailAgent
    from dev_agent.agents.anime_agent import AnimeAgent
    from dev_agent.orchestrator.planner import Planner

    _orig_analyse = GitHubAnalyser.analyse

    async def analyse_with_preamble(self, files, query):
        orig_create = self.client.chat.completions.create

        async def create_with_preamble(*args, **kwargs):
            if "messages" in kwargs:
                kwargs["messages"] = with_system_preamble(kwargs["messages"])
            return await orig_create(*args, **kwargs)

        self.client.chat.completions.create = create_with_preamble
        try:
            return await _orig_analyse(self, files, query)
        finally:
            self.client.chat.completions.create = orig_create

    GitHubAnalyser.analyse = analyse_with_preamble

    _orig_pick = EmailAgent._pick_highlight

    async def pick_with_preamble(self, query, emails):
        orig_create = self.client.chat.completions.create

        async def create_with_preamble(*args, **kwargs):
            if "messages" in kwargs:
                kwargs["messages"] = with_system_preamble(kwargs["messages"])
            return await orig_create(*args, **kwargs)

        self.client.chat.completions.create = create_with_preamble
        try:
            return await _orig_pick(self, query, emails)
        finally:
            self.client.chat.completions.create = orig_create

    EmailAgent._pick_highlight = pick_with_preamble

    _orig_recommend = AnimeAgent._recommend_anime
    _orig_critique = AnimeAgent.critique_suggestion

    async def recommend_with_preamble(self, query):
        orig_create = self.client.chat.completions.create

        async def create_with_preamble(*args, **kwargs):
            if "messages" in kwargs:
                kwargs["messages"] = with_system_preamble(kwargs["messages"])
            return await orig_create(*args, **kwargs)

        self.client.chat.completions.create = create_with_preamble
        try:
            return await _orig_recommend(self, query)
        finally:
            self.client.chat.completions.create = orig_create

    async def critique_with_preamble(self, anime_title, user_reason):
        orig_create = self.client.chat.completions.create

        async def create_with_preamble(*args, **kwargs):
            if "messages" in kwargs:
                kwargs["messages"] = with_system_preamble(kwargs["messages"])
            return await orig_create(*args, **kwargs)

        self.client.chat.completions.create = create_with_preamble
        try:
            return await _orig_critique(self, anime_title, user_reason)
        finally:
            self.client.chat.completions.create = orig_create

    AnimeAgent._recommend_anime = recommend_with_preamble
    AnimeAgent.critique_suggestion = critique_with_preamble

    _orig_decide = Planner.decide_agents

    async def decide_with_preamble(self, query):
        orig_create = self.client.chat.completions.create

        async def create_with_preamble(*args, **kwargs):
            if "messages" in kwargs:
                kwargs["messages"] = with_system_preamble(kwargs["messages"])
            return await orig_create(*args, **kwargs)

        self.client.chat.completions.create = create_with_preamble
        try:
            return await _orig_decide(self, query)
        finally:
            self.client.chat.completions.create = orig_create

    Planner.decide_agents = decide_with_preamble

    _llm_hooks_installed = True
