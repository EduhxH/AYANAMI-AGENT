import httpx
from typing import List, Dict, Optional


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

        return None

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
                    (".py", ".js", ".ts", ".tsx", ".go", ".java", ".md")
                ):
                    content_response = await client.get(
                        item["download_url"],
                        headers=self.headers,
                    )
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
