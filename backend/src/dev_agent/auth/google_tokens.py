import httpx

from dev_agent.auth.oauth_google import GoogleOAuth
from dev_agent.database.models.user import UserInDB
from dev_agent.database.repositories.users import UsersRepository


async def refresh_google_access_token(refresh_token: str) -> dict:
    oauth = GoogleOAuth()
    settings = oauth.settings
    async with httpx.AsyncClient() as client:
        response = await client.post(
            oauth.TOKEN_URL,
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        return response.json()


async def ensure_fresh_google_token(
    user: UserInDB,
    users_repo: UsersRepository,
) -> str | None:
    """
    Devolve um access token válido para a Gmail API.
    Renova automaticamente se existir refresh_token.
    """
    if not user.google_token:
        return None

    if not user.google_refresh_token:
        return user.google_token

    data = await refresh_google_access_token(user.google_refresh_token)
    if "error" in data:
        return user.google_token

    new_access = data.get("access_token")
    if not new_access:
        return user.google_token

    await users_repo.update_google_token(
        user.id,
        new_access,
        user.google_refresh_token,
    )
    return new_access
