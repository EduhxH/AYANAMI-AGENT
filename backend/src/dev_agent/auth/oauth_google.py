import httpx
from urllib.parse import urlencode
from typing import Optional
from fastapi import Request
from dev_agent.core.config import get_settings


class GoogleOAuth:
    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self):
        self.settings = get_settings()

    def get_authorization_url(
        self,
        state: str | None = None,
        request: Optional[Request] = None,
    ) -> str:
        redirect_uri = self.settings.google_redirect_uri
        if request and redirect_uri.startswith(("http://localhost", "https://localhost", "http://127.0.0.1", "https://127.0.0.1")):
            redirect_uri = f"{str(request.base_url).rstrip('/')}" \
                "/auth/callback/google"

        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send",
            "access_type": "offline",   # para receber refresh_token
            "prompt": "consent",
        }
        if state:
            params["state"] = state
        query = urlencode(params)
        return f"{self.AUTHORIZE_URL}?{query}"

    async def exchange_code_for_token(self, code: str) -> dict:
        """
        Google returns both an access token and a refresh token.
The access token expires in 1 hour.
The refresh token allows you to obtain a new access token without logging in.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.settings.google_client_id,
                    "client_secret": self.settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.settings.google_redirect_uri,
                },
            )
            return response.json()  

    async def get_user_email(self, access_token: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.USER_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            return response.json()["email"]