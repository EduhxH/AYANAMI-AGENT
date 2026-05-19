import httpx
from urllib.parse import urlencode
from typing import Optional
from fastapi import Request
from dev_agent.core.config import get_settings


class GitHubOAuth:
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_URL = "https://api.github.com/user"

    def __init__(self):
        self.settings = get_settings()

    def get_authorization_url(
        self,
        state: str | None = None,
        request: Optional[Request] = None,
    ) -> str:
        """
      Generates the URL to which the frontend redirects the user.
The user goes to GitHub and authorizes the app.
        """
        redirect_uri = self.settings.github_redirect_uri
        if request and redirect_uri.startswith(("http://localhost", "https://localhost", "http://127.0.0.1", "https://127.0.0.1")):
            redirect_uri = f"{str(request.base_url).rstrip('/')}" \
                "/auth/callback/github"

        params = {
            "client_id": self.settings.github_client_id,
            "redirect_uri": redirect_uri,
            "scope": "repo user:email delete_repo",
        }
        if state:
            params["state"] = state
        query = urlencode(params)
        return f"{self.AUTHORIZE_URL}?{query}"

    async def exchange_code_for_token(self, code: str) -> str:
        """
        Replace the temporary code (that GitHub gave us) with a permanent token.
This code can only be used once.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.settings.github_client_id,
                    "client_secret": self.settings.github_client_secret,
                    "code": code,
                    "redirect_uri": self.settings.github_redirect_uri,
                },
            )
            data = response.json()
            
            if "error" in data:
                raise ValueError(f"GitHub OAuth erro: {data['error_description']}")
            
            return data["access_token"]

    async def get_user_info(self, token: str) -> dict:
        """Uses the token to obtain user profile information from GitHub."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_URL,
                headers={"Authorization": f"Bearer {token}"},
            )
            return response.json()