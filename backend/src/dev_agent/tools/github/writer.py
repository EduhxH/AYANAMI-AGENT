import re
import base64
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
        print(f"===> ENTRANDO NA CRIAÇÃO DE REPO (writer): name={name!r}, owner={owner!r}, private={private}")
        # Sanitize: strip whitespace and remove characters invalid for GitHub repo names
        name = re.sub(r"[^a-zA-Z0-9_.-]", "-", name.strip()).strip("-")
        if not name:
            raise ValueError("Nome do repositório não fornecido ou inválido após sanitização.")

        owner = owner or self.github_username
        if not owner:
            raise ValueError(
                "Os dados da sua conta vinculada não foram fornecidos no contexto desta sessão."
            )

        payload: dict = {
            "name": name,
            "private": bool(private),
            "auto_init": bool(auto_init),
        }
        if description:
            payload["description"] = str(description)

        if owner and owner != self.github_username:
            url = f"{self.BASE_URL}/orgs/{owner}/repos"
        else:
            url = f"{self.BASE_URL}/user/repos"

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)

            # Safe JSON parse — never crash if GitHub returns non-JSON (e.g. 5xx HTML)
            try:
                content = response.json()
            except Exception:
                content = {}

            if response.status_code not in (201, 202):
                # Expose the raw server error without LLM masking
                api_message = content.get("message") or response.text
                raise ValueError(
                    f"GitHub API error {response.status_code}: {api_message}"
                )
            return content

    async def delete_repo(self, owner: Optional[str], repo: str) -> None:
        if not repo:
            raise ValueError("Nome do repositório não fornecido.")

        owner = owner or self.github_username
        if not owner:
            raise ValueError(
                "Os dados da sua conta vinculada não foram fornecidos no contexto desta sessão."
            )

        url = f"{self.BASE_URL}/repos/{owner}/{repo}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers)
            if response.status_code != 204:
                content = None
                try:
                    content = response.json()
                except ValueError:
                    content = {"message": response.text}
                raise ValueError(
                    f"Erro ao deletar repositório: {response.status_code} — {content.get('message', response.text)}"
                )

    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str = "Create/update file via Ayanami Agent",
        sha: Optional[str] = None,
    ) -> dict:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        
        # Base64 encode content
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        payload = {
            "message": message,
            "content": encoded_content,
        }
        if sha:
            payload["sha"] = sha
            
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=self.headers, json=payload)
            
            try:
                res_json = response.json()
            except Exception:
                res_json = {}
                
            if response.status_code not in (200, 201):
                api_message = res_json.get("message") or response.text
                raise ValueError(
                    f"GitHub API error {response.status_code} writing file: {api_message}"
                )
            return res_json
