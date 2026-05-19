import re

from dev_agent.agents.base_agent import BaseAgent
from dev_agent.core.models import AgentType, AgentResult
from dev_agent.tools.github.reader import GitHubReader, LocalRepoReader
from dev_agent.tools.github.writer import GitHubWriter
from dev_agent.core.config import get_settings
from dev_agent.tools.github.analyser import GitHubAnalyser

_STOP_WORDS = {
    "meu", "minha", "meus", "minhas", "o", "a", "os", "as", "de", "do", "da",
    "no", "na", "um", "uma", "ver", "veja", "analisa", "analise", "analizar",
    "repositorio", "repositório", "repo", "github", "codigo", "código",
    "projeto", "por", "favor", "please", "the", "my", "see", "look", "at",
}


class GitHubAgent(BaseAgent):
    agent_type = AgentType.GITHUB

    def __init__(self, token: str | None, github_username: str | None = None):
        self.token = token
        self.github_username = github_username

    async def run(self, query: str) -> AgentResult:
        settings = get_settings()

        if self.token:
            reader = GitHubReader(self.token)
            writer = GitHubWriter(self.token, github_username=self.github_username)
        else:
            reader = LocalRepoReader(settings.local_repo_root if hasattr(settings, 'local_repo_root') else None)
            writer = None

        try:
            if self._is_create_repo_request(query):
                if not self.token:
                    return self.failure(
                        "Os dados da sua conta vinculada não foram fornecidos no contexto desta sessão."
                    )
                return await self._create_repository(query, writer)

            analyser = GitHubAnalyser()

            repo_name = await self._resolve_repo(query, reader)
            if not repo_name:
                return self.failure(
                    "Não consegui identificar o repositório."
                )

            files = await reader.get_repo_files(repo_name)
            if not files:
                return self.failure(
                    f"O repositório {repo_name} não tem ficheiros de código reconhecidos na raiz."
                )

            analysis = await analyser.analyse(files, query)

            return self.success(
                {
                    "repo": repo_name,
                    "files_analysed": len(files),
                    "issues": analysis.get("issues", []),
                    "suggestions": analysis.get("suggestions", []),
                    "quality_score": analysis.get("quality_score"),
                }
            )
        except Exception as e:
            return self.failure(str(e))

    async def _resolve_repo(self, query: str, reader: GitHubReader) -> str | None:
        explicit = re.search(r"([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)", query)
        if explicit:
            return explicit.group(0)

        hint = self._extract_repo_name_hint(query)
        if not hint:
            return None

        username = self.github_username
        if not username and hasattr(reader, "get_authenticated_login"):
            username = await reader.get_authenticated_login()

        return await reader.find_repo_by_name(hint, username)

    def _is_create_repo_request(self, query: str) -> bool:
        q = query.lower()
        return any(
            phrase in q
            for phrase in (
                "crie", "criar", "novo repositório", "novo repo", "create repo", "create repository"
            )
        )

    async def _create_repository(self, query: str, writer: GitHubWriter) -> AgentResult:
        name = self._extract_repo_name_hint(query)
        if not name:
            return self.failure("Nome do repositório não identificado.")

        visibility = self._resolve_repository_visibility(query)
        owner = self.github_username

        try:
            result = await writer.create_repo(
                name=name,
                private=visibility == "private",
                owner=owner,
            )
            return self.success(
                {
                    "repo": result.get("full_name"),
                    "private": result.get("private"),
                    "html_url": result.get("html_url"),
                }
            )
        except Exception as exc:
            return self.failure(str(exc))

    def _resolve_repository_visibility(self, query: str) -> str:
        q = query.lower()
        private_indicators = (
            "não deixe público",
            "nao deixe publico",
            "privado",
            "private",
            "não público",
            "nao publico",
            "não publíco",
        )
        for phrase in private_indicators:
            if phrase in q:
                return "private"
        return "public"

    def _extract_repo_name_hint(self, query: str) -> str | None:
        patterns = [
            r"reposit[oó]rio\s+([a-zA-Z0-9_.-]+)",
            r"chamad[oó](?:\s+de)?\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?",
            r"chamado\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?",
            r"repo\s+([a-zA-Z0-9_.-]+)",
            r"projecto\s+([a-zA-Z0-9_.-]+)",
            r"projeto\s+([a-zA-Z0-9_.-]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                name = match.group(1).lower()
                if name not in _STOP_WORDS:
                    return match.group(1)

        words = re.findall(r"[a-zA-Z0-9_.-]+", query)
        candidates = [w for w in words if w.lower() not in _STOP_WORDS and len(w) >= 3]
        if candidates:
            return candidates[-1]

        return None
