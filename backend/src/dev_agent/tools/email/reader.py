import httpx
from typing import List, Dict, Callable, Awaitable, Optional

TokenRefreshCallback = Callable[[], Awaitable[str]]


class GmailReader:
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

    async def get_recent_emails(self, max_results: int = 10) -> List[Dict]:
        """Busca os emails mais recentes da caixa de entrada."""
        async with httpx.AsyncClient() as client:
            response = await self._request_with_retry(
                client,
                "GET",
                f"{self.BASE_URL}/users/me/messages",
                params={"maxResults": max_results, "labelIds": "INBOX"},
            )

            if response.status_code != 200:
                raise ValueError(self._gmail_error_message(response))

            messages = response.json().get("messages", [])
            emails = []

            for msg in messages[:max_results]:
                detail = await self._request_with_retry(
                    client,
                    "GET",
                    f"{self.BASE_URL}/users/me/messages/{msg['id']}",
                    params={
                        "format": "metadata",
                        "metadataHeaders": ["From", "Subject"],
                    },
                )

                if detail.status_code != 200:
                    continue

                detail_data = detail.json()
                headers_dict = {
                    h["name"]: h["value"]
                    for h in detail_data.get("payload", {}).get("headers", [])
                }

                emails.append(
                    {
                        "id": msg["id"],
                        "from": headers_dict.get("From", "Desconhecido"),
                        "subject": headers_dict.get("Subject", "Sem assunto"),
                        "snippet": detail_data.get("snippet", ""),
                    }
                )

            return emails
