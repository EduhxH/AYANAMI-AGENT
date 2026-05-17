import httpx
from typing import List, Dict, Optional
import io
import zipfile
import base64


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

        # Fallback: use GitHub search API to find public repositories by name
        async with httpx.AsyncClient() as client:
            q = f"{name_hint} in:name"
            response = await client.get(
                f"{self.BASE_URL}/search/repositories",
                headers=self.headers,
                params={"q": q, "per_page": 5, "sort": "stars", "order": "desc"},
            )
            if response.status_code == 200:
                items = response.json().get("items", [])
                if items:
                    return items[0]["full_name"]

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
