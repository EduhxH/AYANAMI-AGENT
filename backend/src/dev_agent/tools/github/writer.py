import httpx
from typing import Optional


class GitHubWriter:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, github_username: Optional[str] = None):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        self.github_username = github_username

    async def create_repo(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = False,
        owner: Optional[str] = None,
        auto_init: bool = True,
    ) -> dict:
        if not name:
            raise ValueError("Nome do repositório não fornecido.")

        owner = owner or self.github_username
        if not owner:
            raise ValueError(
                "Os dados da sua conta vinculada não foram fornecidos no contexto desta sessão."
            )

        payload = {
            "name": name,
            "private": private,
            "auto_init": auto_init,
        }
        if description:
            payload["description"] = description

        if owner and owner != self.github_username:
            url = f"{self.BASE_URL}/orgs/{owner}/repos"
        else:
            url = f"{self.BASE_URL}/user/repos"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            content = response.json()
            if response.status_code not in (201, 202):
                raise ValueError(
                    f"Erro ao criar repositório: {response.status_code} — {content.get('message', response.text)}"
                )
            return content
