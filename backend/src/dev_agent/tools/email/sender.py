import httpx
import base64
from typing import Optional, Callable, Awaitable
from email.mime.text import MIMEText

TokenRefreshCallback = Callable[[], Awaitable[str]]


class GmailSender:
    BASE_URL = "https://gmail.googleapis.com/gmail/v1"

    def __init__(
        self,
        token: str,
        on_token_refresh: Optional[TokenRefreshCallback] = None,
    ):
        self.token = token
        self.on_token_refresh = on_token_refresh

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}"}

    async def _request_with_retry(self, client: httpx.AsyncClient, method: str, url: str, **kwargs):
        response = await client.request(method, url, headers=self._headers(), **kwargs)

        if response.status_code in (401, 403) and self.on_token_refresh:
            new_token = await self.on_token_refresh()
            if new_token and new_token != self.token:
                self.token = new_token
                response = await client.request(
                    method, url, headers=self._headers(), **kwargs
                )

        return response

    def _gmail_error_message(self, response: httpx.Response) -> str:
        try:
            body = response.json()
            msg = body.get("error", {}).get("message", response.text[:300])
        except Exception:
            msg = response.text[:300]

        if response.status_code == 403:
            return (
                f"Gmail recusou o acesso (403): {msg}. "
                "Activa a Gmail API no Google Cloud Console e volta a ligar o Gmail "
                "em Definições (desliga e liga de novo para renovar permissões)."
            )
        if response.status_code == 401:
            return (
                f"Token Gmail expirado (401). Volta a ligar o Gmail em Definições. Detalhe: {msg}"
            )
        return f"Erro Gmail: {response.status_code} — {msg}"

    def _create_message(
        self,
        to: str,
        subject: str,
        body: str,
        reply_to: Optional[str] = None,
    ) -> dict:
        """Cria uma mensagem MIME e a codifica em base64 para a API do Gmail."""
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        if reply_to:
            message["In-Reply-To"] = reply_to
            message["References"] = reply_to
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return {"raw": raw_message}

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        reply_to: Optional[str] = None,
    ) -> dict:
        """Envia um email através da API do Gmail."""
        message = self._create_message(to, subject, body, reply_to)
        
        async with httpx.AsyncClient() as client:
            response = await self._request_with_retry(
                client,
                "POST",
                f"{self.BASE_URL}/users/me/messages/send",
                json=message,
            )

            if response.status_code != 200:
                raise ValueError(self._gmail_error_message(response))

            result = response.json()
            return {
                "message_id": result.get("id"),
                "thread_id": result.get("threadId"),
                "success": True,
                "message": "Email enviado com sucesso!"
            }
