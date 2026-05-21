import re
import httpx
from typing import Optional, List
from groq import AsyncGroq

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

    async def run(self, query: str, history: Optional[List[dict]] = None) -> AgentResult:
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
                print(f"[GITHUB_AGENT] Nenhuma referência específica de repositório detectada; executando operação global")
                try:
                    accessible_repos = await reader.list_accessible_repos()
                except Exception as exc:
                    print(f"[GITHUB_AGENT] Erro ao listar repositórios acessíveis: {exc}")
                    return self.failure(f"Não foi possível listar repositórios acessíveis: {exc}")

                if not accessible_repos:
                    print(f"[GITHUB_AGENT] Nenhum repositório acessível encontrado")
                    return self.failure(
                        "Nenhum repositório acessível encontrado para operação global."
                    )

                repo_list = [repo.get("full_name", repo.get("name")) for repo in accessible_repos]
                print(f"[GITHUB_AGENT] Operação global aplicada: {len(repo_list)} repositórios encontrados")
                return self.success(
                    {
                        "global_operation": True,
                        "repo_count": len(repo_list),
                        "repositories": repo_list,
                        "message": "Nenhuma referência específica a um repositório foi detectada; mostrando repositórios acessíveis.",
                    }
                )

            print(f"[GITHUB_AGENT] Repositório identificado: {repo_name}")
            repo_context = await self._build_repo_context(repo_name, reader)
            files = await reader.get_repo_files(repo_name)
            if not files:
                print(f"[GITHUB_AGENT] Nenhum arquivo encontrado no repositório")
                return self.failure(
                    f"O repositório {repo_name} não tem ficheiros de código reconhecidos na raiz."
                )

            analysis = await analyser.analyse(files, query)

            print(f"[GITHUB_AGENT] Análise completada com sucesso")
            context_text = self._serialize_repo_context(repo_context)
            return self.success(
                {
                    "repo": repo_name,
                    "files_analysed": len(files),
                    "issues": analysis.get("issues", []),
                    "suggestions": analysis.get("suggestions", []),
                    "quality_score": analysis.get("quality_score"),
                    "repo_context": repo_context,
                    "repo_context_text": context_text,
                }
            )
        except ValueError as e:
            print(f"[GITHUB_AGENT] ValueError capturada: {e}")
            return self.failure(f"[RAW ERROR] {e}")
        except Exception as e:
            print(f"[GITHUB_AGENT] Exception inesperada capturada: {type(e).__name__}: {e}")
            return self.failure(f"[UNEXPECTED ERROR] {type(e).__name__}: {e}")

    async def _resolve_repo(self, query: str, reader: GitHubReader) -> str | None:
        explicit_url = re.search(
            r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(?:[/?\s]|$)",
            query,
            re.IGNORECASE,
        )
        if explicit_url:
            owner = explicit_url.group(1)
            repo_name = explicit_url.group(2)
            print(f"[GITHUB_AGENT] URL GitHub detectada, retornando repo '{owner}/{repo_name}'")
            return f"{owner}/{repo_name}"

        explicit_owner_repo = re.search(r"\b([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)\b", query)
        if explicit_owner_repo:
            owner = explicit_owner_repo.group(1)
            repo_name = explicit_owner_repo.group(2)
            print(f"[GITHUB_AGENT] Nome owner/repo detectado, retornando repo '{owner}/{repo_name}'")
            return f"{owner}/{repo_name}"

        known_repo = await self._find_known_repo_in_query(query, reader)
        if known_repo:
            print(f"[GITHUB_AGENT] Repositório conhecido detectado na query: {known_repo}")
            return known_repo

        hint = self._extract_repo_name_hint(query)
        if not hint:
            return None

        username = self.github_username
        if not username and hasattr(reader, "get_authenticated_login"):
            username = await reader.get_authenticated_login()

        return await reader.find_repo_by_name(hint, username)

    async def _find_known_repo_in_query(self, query: str, reader: GitHubReader) -> str | None:
        try:
            repos = await reader.list_accessible_repos()
        except Exception as exc:
            print(f"[GITHUB_AGENT] Falha ao buscar repositórios acessíveis para correspondência de query: {exc}")
            return None

        if not repos:
            return None

        candidates = []
        for repo in repos:
            name = repo.get("name", "")
            full_name = repo.get("full_name", "")
            if self._query_contains_repo_name(query, full_name):
                candidates.append((full_name, len(full_name)))
            elif self._query_contains_repo_name(query, name):
                target = full_name or name
                candidates.append((target, len(name)))

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[1], reverse=True)
        return candidates[0][0]

    def _query_contains_repo_name(self, query: str, repo_name: str) -> bool:
        if not repo_name:
            return False
        pattern = rf"(?<![A-Za-z0-9_.-]){re.escape(repo_name)}(?![A-Za-z0-9_.-])"
        return bool(re.search(pattern, query, re.IGNORECASE))

    async def _build_repo_context(self, repo: str, reader: GitHubReader) -> dict:
        summary = {}
        readme = None
        file_tree = []
        config_files = []
        main_entry_files = []

        try:
            summary = await reader.get_repo_summary(repo)
        except Exception as exc:
            print(f"[GITHUB_AGENT] Falha ao obter resumo do repositório: {exc}")

        try:
            root_contents = await reader.get_repo_root_contents(repo)
            file_tree = [f"{item.get('type')} {item.get('name')}" for item in root_contents]
            entry_map = {item.get("name", "").lower(): item for item in root_contents if item.get("type") == "file"}

            for candidate in ("readme.md", "readme"):
                if candidate in entry_map:
                    readme = await reader.get_repo_file_content(repo, entry_map[candidate]["path"])
                    break

            config_candidates = [
                "package.json",
                "requirements.txt",
                "pyproject.toml",
                "go.mod",
                "dockerfile",
            ]
            for name in config_candidates:
                item = entry_map.get(name)
                if item:
                    content = await reader.get_repo_file_content(repo, item["path"])
                    if content is not None:
                        config_files.append({"path": item["path"], "content": content})

            main_candidates = ["main.py", "index.js", "app.py", "src/main.py", "src/index.js"]
            for name in main_candidates:
                item = entry_map.get(name)
                if item:
                    content = await reader.get_repo_file_content(repo, item["path"])
                    if content is not None:
                        main_entry_files.append({"path": item["path"], "content": content})
                    continue

                content = await reader.get_repo_file_content(repo, name)
                if content is not None:
                    main_entry_files.append({"path": name, "content": content})
        except Exception as exc:
            print(f"[GITHUB_AGENT] Falha ao construir contexto de repositório: {exc}")

        result = {
            "summary": summary,
            "readme": readme,
            "file_tree": file_tree,
            "config_files": config_files,
            "main_entry_files": main_entry_files,
        }
        result["repo_context_text"] = self._serialize_repo_context(result)
        return result

    def _serialize_repo_context(self, context: dict) -> str:
        sections = []
        summary = context.get("summary") or {}
        if summary:
            sections.append("REPOSITÓRIO:\n" + "\n".join(
                f"{k}: {v}" for k, v in summary.items() if v is not None
            ))

        if context.get("readme"):
            sections.append("README:\n" + context["readme"].strip())

        if context.get("file_tree"):
            sections.append("Árvore de arquivos na raíz:\n" + "\n".join(context["file_tree"]))

        if context.get("config_files"):
            config_lines = [f"{item['path']}:\n{item['content'].strip()}" for item in context["config_files"]]
            sections.append("Arquivos de configuração detectados:\n" + "\n---\n".join(config_lines))

        if context.get("main_entry_files"):
            main_lines = [f"{item['path']}:\n{item['content'].strip()}" for item in context["main_entry_files"]]
            sections.append("Arquivos de entrada principais:\n" + "\n---\n".join(main_lines))

        return "\n\n".join(sections).strip()

    def _is_create_repo_request(self, query: str) -> bool:
        q = query.lower()
        # Direct phrase matches
        phrases = [
            "faça um repo", "faca um repo", "faça repo", "faca repo",
            "crie um repositório", "crie um repositorio", "crie repo",
            "criar repositório", "criar repositorio", "cria repositório", "cria repositorio",
            "new repo", "new repository", "create repo", "create repository",
            "criar projeto", "criar project", "crie projeto", "crie project",
            "novo repositório", "novo repositorio", "novo repo", "novo projeto",
            "nova repo", "nova repository", "create project", "make repo", "make repository"
        ]
        if any(phrase in q for phrase in phrases):
            return True

        # Verb + target regex matching
        verbs_pattern = r"\b(cria|criar|crie|create|faça|faca|fazer|make|new|novo|nova)\b"
        targets_pattern = r"\b(repo|reposit[oó]rio|repository|projet[oó]|project)\b"
        
        if re.search(verbs_pattern, q) and re.search(targets_pattern, q):
            return True
            
        return False

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

        # Generate README content if requested
        readme_content = await self._generate_readme_content(query)
        print(f"[GITHUB_AGENT] Conteúdo do README gerado: {readme_content!r}")

        # Resolve description:
        # If there's an explicit description request, use it. Otherwise, use a default description.
        description = None
        if "descri" in query.lower() or "description" in query.lower():
            description = self._extract_description_hint(query)
        
        if not description:
            description = f"Repository {name} created by Ayanami Agent."

        try:
            print(f"[GITHUB_AGENT] Chamando writer.create_repo()...")
            result = await writer.create_repo(
                name=name,
                private=visibility == "private",
                owner=owner,
                description=description,
                auto_init=True,
            )
            print(f"[GITHUB_AGENT] create_repo retornou: {result}")
            
            repo_full_name = result.get("full_name")
            repo_owner, repo_name = repo_full_name.split("/")
            
            # If README content is requested, write the README.md file
            if readme_content:
                print(f"[GITHUB_AGENT] Gravando README.md com conteúdo gerado...")
                
                # Fast GET request to find the existing README.md SHA if initialized by auto_init
                existing_sha = None
                try:
                    async with httpx.AsyncClient() as client:
                        url = f"{writer.BASE_URL}/repos/{repo_owner}/{repo_name}/contents/README.md"
                        resp = await client.get(url, headers=writer.headers)
                        if resp.status_code == 200:
                            existing_sha = resp.json().get("sha")
                            print(f"[GITHUB_AGENT] Encontrado SHA existente para README.md: {existing_sha}")
                        else:
                            print(f"[GITHUB_AGENT] README.md não retornado com status 200: {resp.status_code}")
                except Exception as sha_exc:
                    print(f"[GITHUB_AGENT] Falha ao buscar SHA do README.md existente: {sha_exc}")

                try:
                    await writer.create_or_update_file(
                        owner=repo_owner,
                        repo=repo_name,
                        path="README.md",
                        content=readme_content,
                        message="Initialize README.md with generated content",
                        sha=existing_sha,
                    )
                    print(f"[GITHUB_AGENT] README.md gravado com sucesso.")
                except Exception as file_exc:
                    print(f"[GITHUB_AGENT] Falha ao gravar README.md: {file_exc}")
            
            return self.success(
                {
                    "repo": repo_full_name,
                    "private": result.get("private"),
                    "html_url": result.get("html_url"),
                    "readme_created": bool(readme_content),
                }
            )
        except ValueError as exc:
            # Re-raise raw API error — do NOT let the LLM rephrase or hallucinate
            return self.failure(f"[RAW ERROR] {exc}")
        except Exception as exc:
            return self.failure(f"[UNEXPECTED ERROR] {type(exc).__name__}: {exc}")

    async def _generate_readme_content(self, query: str) -> str | None:
        q = query.lower()
        if "readme" not in q and "leia-me" not in q and "leiame" not in q:
            return None

        system_prompt = (
            "Você é um especialista em extração e geração de conteúdo para arquivos README.md do GitHub.\n"
            "Dada a instrução de um usuário, identifique se ele solicitou que algum conteúdo ou informação específica "
            "seja adicionado ao README do repositório.\n"
            "Se o usuário solicitou uma frase famosa, uma piada, uma citação ou qualquer outro conteúdo criativo "
            "(ex: 'frase mais famosa do darth vader' ou 'piada de programador'), você DEVE gerar e retornar esse conteúdo real correspondente "
            "(ex: 'No, I am your father' ou a piada gerada).\n"
            "Se o usuário apenas forneceu um texto simples literal para colocar no readme (ex: 'coloque \"funcionou\" no readme'), "
            "retorne esse texto de forma limpa.\n"
            "Retorne APENAS o conteúdo final em formato Markdown que deve ser gravado no arquivo README.md. "
            "Não inclua explicações, comentários, introduções ou formatação adicional fora do Markdown gerado."
        )
        
        try:
            settings = get_settings()
            client = AsyncGroq(api_key=settings.groq_api_key)
            
            response = await client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
            )
            content = response.choices[0].message.content.strip()
            return content if content else None
        except Exception as exc:
            print(f"[GITHUB_AGENT] Erro ao gerar conteúdo do README via LLM: {exc}")
            # Fallback extraction: try to extract whatever was found in the query description hint
            desc = self._extract_description_hint(query)
            return desc

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

        # Check for negation patterns indicating NOT public:
        # e.g., "não público", "nao publico", "n publico", "no public"
        # "não deixe público", "nao deixe ele publico", "n deixe ele publico", "n deixa publico"
        # We look for a negation word (não, nao, n, no, not, sem) followed by something and then public
        negation_words = r"\b(n[ãa]o|nao|n|no|not|sem)\b"
        public_words = r"\b(publ[ií]c|p[uú]blico)\b"
        
        # If there is a negation followed by public (with optional words like "deixe", "ele", "ser" in between)
        if re.search(rf"{negation_words}.*?{public_words}", q):
            return "private"

        # Shorthand or direct matches
        direct_private_phrases = [
            "não deixe público", "nao deixe publico", "n deixe publico", "n deixe ele publico",
            "não público", "nao publico", "n publico", "não publíco",
            "sem ser publico", "sem ser público", "not public", "dont make it public", "don't make it public"
        ]
        if any(phrase in q for phrase in direct_private_phrases):
            return "private"

        return "public"

    def _extract_repo_name_hint(self, query: str) -> str | None:
        # 1. First, check if there is a pattern like `nome de "teste923"` or `nome: "teste923"` or `nome "teste923"`
        # or simply `nome de teste923`.
        # Connectors can be: chamado, chamada, denominado, nome, como, etc.
        connector = r"(?:chamad[oó]|chamada|denominado|nome|como)"
        
        # Pattern checking for connector + value (optionally quoted)
        match_conn = re.search(rf"{connector}(?:\s+de)?\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?", query, re.IGNORECASE)
        if match_conn:
            name = match_conn.group(1)
            if name and name.lower() not in _STOP_WORDS:
                return name

        # 2. Next, check if there's any single word inside quotes (double or single quotes)
        # E.g. crie um repo "teste923"
        quoted_matches = re.findall(r"[\"']([a-zA-Z0-9_.-]+)[\"']", query)
        for name in quoted_matches:
            if name and name.lower() not in _STOP_WORDS:
                return name

        # 3. Check for creation verb + target repo noun followed by the name
        # E.g. "faça um repo teste923", "criar projeto teste923"
        verbs = r"(?:cria|criar|crie|create|faça|faca|fazer|make)"
        targets = r"(?:reposit[oó]rio|repo|projeto|project)"
        match_verb_target = re.search(rf"{verbs}\s+(?:um\s+)?{targets}\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?", query, re.IGNORECASE)
        if match_verb_target:
            name = match_verb_target.group(1)
            if name and name.lower() not in _STOP_WORDS:
                return name

        # 4. Check for target noun followed by the name
        # E.g. "repo teste923", "projeto teste923"
        match_target = re.search(rf"{targets}\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?", query, re.IGNORECASE)
        if match_target:
            name = match_target.group(1)
            if name and name.lower() not in _STOP_WORDS:
                return name

        # 5. Check for creation verb followed by the name
        # E.g. "cria teste923"
        match_verb = re.search(rf"{verbs}\s+[\"']?([a-zA-Z0-9_.-]+)[\"']?", query, re.IGNORECASE)
        if match_verb:
            name = match_verb.group(1)
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
