import httpx
from typing import List, Dict, Optional
import io
import zipfile
import base64
import os
from typing import Iterable


class GitHubReader:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_authenticated_login(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/user",
                headers=self.headers,
            )
            if response.status_code != 200:
                raise ValueError(
                    f"Não foi possível obter o utilizador GitHub: {response.status_code}"
                )
            return response.json()["login"]

    async def list_accessible_repos(self, max_repos: int = 100) -> List[Dict]:
        """Repositórios do utilizador autenticado (owner/collaborator)."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/user/repos",
                headers=self.headers,
                params={
                    "per_page": min(max_repos, 100),
                    "sort": "updated",
                    "affiliation": "owner,collaborator,organization_member",
                },
            )
            if response.status_code != 200:
                raise ValueError(
                    f"Erro ao listar repositórios: {response.status_code} — {response.text[:200]}"
                )
            return response.json()

    async def find_repo_by_name(
        self, name_hint: str, username: Optional[str] = None
    ) -> Optional[str]:
        """Procura owner/repo pelo nome (ex: 'fullstack' -> 'user/fullstack')."""
        hint = name_hint.lower().strip()
        repos = await self.list_accessible_repos()

        exact = [r for r in repos if r["name"].lower() == hint]
        if exact:
            return exact[0]["full_name"]

        partial = [r for r in repos if hint in r["name"].lower()]
        if len(partial) == 1:
            return partial[0]["full_name"]
        if partial:
            partial.sort(key=lambda r: r.get("updated_at", ""), reverse=True)
            return partial[0]["full_name"]

        if username:
            candidate = f"{username}/{name_hint}"
            if await self.repo_exists(candidate):
                return candidate

        # Do NOT fallback to public GitHub search. Only consider repos
        # accessible to the authenticated user or the explicit username
        # candidate. This prevents returning third-party repositories
        # when the user requested a repo that doesn't exist in their
        # context.
        return None

    async def get_repo_summary(self, repo: str) -> Dict:
        """Return basic metadata and README excerpt for a repo."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.BASE_URL}/repos/{repo}", headers=self.headers)
            if resp.status_code != 200:
                raise ValueError(f"Erro ao obter metadados do repo: {resp.status_code}")
            meta = resp.json()

            # Try README
            readme = None
            r = await client.get(f"{self.BASE_URL}/repos/{repo}/readme", headers=self.headers)
            if r.status_code == 200:
                rd = r.json()
                if rd.get("content"):
                    try:
                        content = base64.b64decode(rd["content"]).decode("utf-8", errors="ignore")
                        readme = content[:2000]
                    except Exception:
                        readme = None

            return {
                "full_name": meta.get("full_name"),
                "description": meta.get("description"),
                "stars": meta.get("stargazers_count"),
                "language": meta.get("language"),
                "readme": readme,
                "html_url": meta.get("html_url"),
            }

    async def get_repo_archive_files(self, repo: str) -> List[Dict]:
        """Download the repository zipball and extract text and small images for analysis."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.BASE_URL}/repos/{repo}/zipball", headers=self.headers)
            if response.status_code != 200:
                raise ValueError("Não foi possível descarregar o arquivo do repositório")

            z = zipfile.ZipFile(io.BytesIO(response.content))
            files: List[Dict] = []
            for info in z.infolist():
                name = info.filename
                if info.is_dir():
                    continue
                lower = name.lower()
                try:
                    with z.open(info) as fp:
                        data = fp.read()
                        if lower.endswith((".md", ".py", ".js", ".ts", ".txt", ".java", ".go")):
                            text = data.decode("utf-8", errors="ignore")
                            files.append({"name": name.split("/", 1)[-1], "path": name, "content": text[:3000]})
                        elif lower.endswith((".png", ".jpg", ".jpeg", ".gif")):
                            b64 = base64.b64encode(data).decode("ascii")
                            files.append({"name": name.split("/", 1)[-1], "path": name, "content": f"[IMAGE base64:{len(b64)}]"})
                        elif lower.endswith(".zip"):
                            # skip nested zips
                            files.append({"name": name.split("/", 1)[-1], "path": name, "content": "ZIP file"})
                except Exception:
                    continue
                if len(files) >= 20:
                    break
            return files

    async def repo_exists(self, repo: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{repo}",
                headers=self.headers,
            )
            return response.status_code == 200

    async def get_repo_files(self, repo: str, path: str = "") -> List[Dict]:
        """
        Busca os ficheiros de um repositório.
        repo = "owner/repo-name"
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/repos/{repo}/contents/{path}",
                headers=self.headers,
            )

            if response.status_code == 404:
                raise ValueError(f"Repositório não encontrado: {repo}")
            if response.status_code != 200:
                raise ValueError(
                    f"Erro ao aceder ao repo {repo}: {response.status_code} — {response.text[:200]}"
                )

            items = response.json()
            if isinstance(items, dict):
                items = [items]

            files = []

            for item in items:
                if item.get("type") == "file" and item["name"].endswith(
                    (".py", ".js", ".ts", ".tsx", ".go", ".java", ".md", ".txt", ".json", ".yaml", ".yml", ".zip", ".png", ".jpg", ".jpeg", ".gif")
                ):
                    content_response = await client.get(
                        item["download_url"],
                        headers=self.headers,
                    )
                    if item["name"].lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                        size = len(content_response.content)
                        files.append({"name": item["name"], "path": item["path"], "content": f"[IMAGE {item['name']} size={size}]"})
                    elif item["name"].lower().endswith(".zip"):
                        try:
                            z = zipfile.ZipFile(io.BytesIO(content_response.content))
                            for zi in z.infolist()[:10]:
                                if zi.is_dir():
                                    continue
                                with z.open(zi) as fp:
                                    try:
                                        text = fp.read().decode("utf-8", errors="ignore")
                                        files.append({"name": zi.filename.split("/",1)[-1], "path": zi.filename, "content": text[:2000]})
                                    except Exception:
                                        continue
                        except Exception:
                            files.append({"name": item["name"], "path": item["path"], "content": "ZIP file (could not extract)"})
                    else:
                        files.append(
                            {
                                "name": item["name"],
                                "path": item["path"],
                                "content": content_response.text[:3000],
                            }
                        )
                elif item.get("type") == "dir" and len(files) < 5:
                    try:
                        sub_files = await self.get_repo_files(repo, item["path"])
                        files.extend(sub_files)
                    except ValueError:
                        pass

            return files[:8]


class LocalRepoReader:
    """Leitor simples que lê um repositório localizado no disco.

    Usa um diretório root (p.ex. definido por `LOCAL_REPO_ROOT` ou cwd)
    e procura por diretórios correspondentes ao nome do repositório.
    """

    def __init__(self, root: Optional[str] = None):
        self.root = root or os.getcwd()

    def _repo_dir_candidates(self, name_hint: str) -> Iterable[str]:
        # procura por pastas cujo nome contenha o hint
        try:
            for entry in os.listdir(self.root):
                full = os.path.join(self.root, entry)
                if os.path.isdir(full) and name_hint.lower() in entry.lower():
                    yield full
        except Exception:
            return

    def repo_exists(self, repo: str) -> bool:
        # repo pode ser 'owner/name' ou 'name'
        name = repo.split("/")[-1]
        path = os.path.join(self.root, name)
        return os.path.isdir(path)

    async def list_accessible_repos(self, max_repos: int = 100) -> List[Dict]:
        repos = []
        try:
            for entry in os.listdir(self.root)[:max_repos]:
                full = os.path.join(self.root, entry)
                if os.path.isdir(full):
                    repos.append({"name": entry, "full_name": entry, "path": full})
        except Exception:
            pass
        return repos

    async def find_repo_by_name(self, name_hint: str, username: Optional[str] = None) -> Optional[str]:
        hint = name_hint.lower().strip()
        # Exact match
        exact_path = os.path.join(self.root, hint)
        if os.path.isdir(exact_path):
            return hint

        # try candidates
        for full in self._repo_dir_candidates(hint):
            return os.path.basename(full)

        # if username provided, try username/name under root
        if username:
            cand = os.path.join(self.root, name_hint)
            if os.path.isdir(cand):
                return name_hint

        return None

    async def get_repo_files(self, repo: str, path: str = "") -> List[Dict]:
        name = repo.split("/")[-1]
        root = os.path.join(self.root, name)
        files = []
        exts = (".py", ".js", ".ts", ".tsx", ".go", ".java", ".md", ".txt", ".json", ".yaml", ".yml")
        if not os.path.isdir(root):
            raise ValueError(f"Repositório local não encontrado: {repo}")

        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                if fn.lower().endswith(exts):
                    try:
                        fp = os.path.join(dirpath, fn)
                        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                            text = f.read(3000)
                        rel = os.path.relpath(fp, root)
                        files.append({"name": fn, "path": rel, "content": text})
                    except Exception:
                        continue
                if len(files) >= 20:
                    break
            if len(files) >= 20:
                break
        return files[:8]
