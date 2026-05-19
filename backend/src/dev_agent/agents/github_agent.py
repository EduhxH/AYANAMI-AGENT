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
        print(f"[GITHUB_AGENT] run() chamado")
        print(f"[GITHUB_AGENT] Query: {query!r}")
        print(f"[GITHUB_AGENT] Token: {'***' if self.token else 'NULL'}")
        print(f"[GITHUB_AGENT] Username: {self.github_username}")
        
        settings = get_settings()

        try:
            # Validação explícita do token do GitHub ao iniciar
            is_delete = self._is_delete_repo_request(query)
            is_create = self._is_create_repo_request(query)
            
            print(f"[GITHUB_AGENT] is_delete_request: {is_delete}")
            print(f"[GITHUB_AGENT] is_create_request: {is_create}")
            
            if is_delete or is_create:
                print(f"[GITHUB_AGENT] Operação de create/delete detectada")
                if not self.token or (isinstance(self.token, str) and self.token.strip() == ""):
                    print(f"[GITHUB_AGENT] Token vazio/nulo detectado - lançando ValueError")
                    raise ValueError("Token do GitHub não encontrado para a sessão atual.")
                print(f"[GITHUB_AGENT] Token validado com sucesso")

            if self.token:
                reader = GitHubReader(self.token)
                writer = GitHubWriter(self.token, github_username=self.github_username)
            else:
                reader = LocalRepoReader(settings.local_repo_root if hasattr(settings, 'local_repo_root') else None)
                writer = None

            if is_delete:
                print(f"[GITHUB_AGENT] Executando _delete_repository")
                return await self._delete_repository(query, writer)

            if is_create:
                print(f"[GITHUB_AGENT] Executando _create_repository")
                return await self._create_repository(query, writer)

            analyser = GitHubAnalyser()

            print(f"[GITHUB_AGENT] Resolvendo nome do repositório...")
            repo_name = await self._resolve_repo(query, reader)
            if not repo_name:
                print(f"[GITHUB_AGENT] Falha ao resolver nome do repositório")
                return self.failure(
                    "Não consegui identificar o repositório."
                )

            print(f"[GITHUB_AGENT] Repositório identificado: {repo_name}")
            files = await reader.get_repo_files(repo_name)
            if not files:
                print(f"[GITHUB_AGENT] Nenhum arquivo encontrado no repositório")
                return self.failure(
                    f"O repositório {repo_name} não tem ficheiros de código reconhecidos na raiz."
                )

            analysis = await analyser.analyse(files, query)

            print(f"[GITHUB_AGENT] Análise completada com sucesso")
            return self.success(
                {
                    "repo": repo_name,
                    "files_analysed": len(files),
                    "issues": analysis.get("issues", []),
                    "suggestions": analysis.get("suggestions", []),
                    "quality_score": analysis.get("quality_score"),
                }
            )
        except ValueError as e:
            print(f"[GITHUB_AGENT] ValueError capturada: {e}")
            return self.failure(f"[RAW ERROR] {e}")
        except Exception as e:
            print(f"[GITHUB_AGENT] Exception inesperada capturada: {type(e).__name__}: {e}")
            return self.failure(f"[UNEXPECTED ERROR] {type(e).__name__}: {e}")

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
        # Match common verbs and phrases that indicate repo creation (Portuguese & English)
        if re.search(r"\b(cria|criar|crie|create|novo|nova)\b", q):
            # If mentions 'novo' ensure it's followed by repo/repositório soon after
            if "novo" in q or "nova" in q:
                if re.search(r"\b(novo|nova)\b.*\b(repo|reposit[oó]rio)\b", q):
                    return True
            # Direct verbs or explicit 'repo' mentions
            if re.search(r"\b(cria|criar|crie|create)\b.*\b(repo|reposit[oó]rio)\b", q):
                return True
            # simple forms like 'cria um repo', 'create repo'
            if re.search(r"\b(cria|criar|crie|create)\b", q) and ("repo" in q or "reposit" in q):
                return True
        # also check for explicit phrases
        return any(phrase in q for phrase in ("novo repositório", "novo repo", "create repo", "create repository"))

    def _is_delete_repo_request(self, query: str) -> bool:
        q = query.lower()
        return any(
            phrase in q
            for phrase in (
                "delete", "deletar", "remover repositório", "remova repositório", "apagar repositório", "delete repo", "delete repository"
            )
        )

    async def _create_repository(self, query: str, writer: GitHubWriter) -> AgentResult:
        print(f"[GITHUB_AGENT] _create_repository() chamado")
        print(f"[GITHUB_AGENT] Query: {query!r}")
        print(f"[GITHUB_AGENT] Writer: {writer}")
        
        name = self._extract_repo_name_hint(query)
        print(f"[GITHUB_AGENT] Nome extraído: {name!r}")
        if not name:
            print(f"[GITHUB_AGENT] Falha ao extrair nome do repositório")
            return self.failure("Nome do repositório não identificado.")

        visibility = self._resolve_repository_visibility(query)
        owner = self.github_username
        
        print(f"[GITHUB_AGENT] Visibilidade: {visibility}")
        print(f"[GITHUB_AGENT] Owner: {owner}")

        # Extract optional description hint from the query (e.g. 'no readme coloque X')
        description = self._extract_description_hint(query)
        print(f"[GITHUB_AGENT] Descrição: {description!r}")

        try:
            print(f"[GITHUB_AGENT] Chamando writer.create_repo()...")
            result = await writer.create_repo(
                name=name,
                private=visibility == "private",
                owner=owner,
                description=description,
            )
            print(f"[GITHUB_AGENT] create_repo retornou: {result}")
            return self.success(
                {
                    "repo": result.get("full_name"),
                    "private": result.get("private"),
                    "html_url": result.get("html_url"),
                }
            )
        except ValueError as exc:
            # Re-raise raw API error — do NOT let the LLM rephrase or hallucinate
            return self.failure(f"[RAW ERROR] {exc}")
        except Exception as exc:
            return self.failure(f"[UNEXPECTED ERROR] {type(exc).__name__}: {exc}")

    async def _delete_repository(self, query: str, writer: GitHubWriter) -> AgentResult:
        name = self._extract_repo_name_hint(query)
        if not name:
            return self.failure("Nome do repositório não identificado.")

        owner = self.github_username
        try:
            await writer.delete_repo(owner=owner, repo=name)
            return self.success({"repo": f"{owner}/{name}", "deleted": True})
        except Exception as exc:
            return self.failure(str(exc))

    def _resolve_repository_visibility(self, query: str) -> str:
        q = query.lower()
        # Robust detection for private intent. Match explicit words or negation patterns
        if "privado" in q or "private" in q:
            return "private"
        # Patterns like: "não deixe público", "nao deixe ele publico", "não deixe-o público"
        if re.search(r"\b(n[ãa]o|nao)\b.*\bdeix(?:e|ar|ando)\b.*\bpublic", q):
            return "private"

        # Shorthand 'n' used as 'não' or variations like 'n deixe publico', 'n publico'
        # We want to detect isolated ' n ' or ' n ' before 'publico'
        if re.search(r"\b[nN]\b\s*(?:deixe|deix|deix-e|deix-o|nao)?\b.*\bpublic", query):
            return "private"

        # Direct negative phrases
        for phrase in ("não deixe público", "nao deixe publico", "não público", "nao publico", "não publíco", "n deixe publico", "n publico", "n deixe ele publico", "sem ser publico"):
            if phrase in q:
                return "private"
        return "public"

    def _extract_repo_name_hint(self, query: str) -> str | None:
        # Try several patterns that commonly indicate a repo name after create/novo/chamado
        # Patterns ordered to prefer explicit connectors (chamado/nome/denominado) and
        # to avoid capturing connector words themselves as the repo name.
        connector = r"(?:chamad[oó]|chamada|chamado|denominado|nome|como)"
        patterns = [
            # cria um repo chamado <name>
            rf"(?:cria|criar|crie|create)\s+(?:um\s+)?(?:reposit[oó]rio|repo)(?:\s+{connector})?\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?",
            # cria '<name>'
            r"(?:cria|criar|crie|create)\s+[\"']([a-zA-Z0-9_.-]+)[\"']",
            # repositório chamado <name>
            rf"reposit[oó]rio(?:\s+{connector})?\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?",
            # chamado <name> / chamad[oó]o de <name>
            rf"{connector}(?:\s+de)?\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?",
            # repo <name>
            r"repo\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?",
            r"projecto\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?",
            r"projeto\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?",
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                name = match.group(1)
                if name and name.lower() not in _STOP_WORDS:
                    return name

        # Fallback: pick the first token that looks like a repo name
        words = re.findall(r"[a-zA-Z0-9_.-]+", query)
        candidates = [w for w in words if w.lower() not in _STOP_WORDS and len(w) >= 3]
        if candidates:
            return candidates[0]

        return None

    def _extract_description_hint(self, query: str) -> str | None:
        """
        Extract an optional description from natural-language instructions such as:
          'no readme coloque funcionou'
          'com descrição meu projeto'
          'description: hello world'
        The extracted text is used as the GitHub repo description field, never as the name.
        """
        patterns = [
            r"no\s+readme\s+(?:coloque|escreva|ponha)\s+(.+)",
            r"com\s+descri[çc][aã]o\s+(.+)",
            r"descri[çc][aã]o[:\s]+(.+)",
            r"description[:\s]+(.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
