from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dev_agent.auth.jwt import decode_token
from dev_agent.auth.oauth_state import verify_oauth_state
from dev_agent.database.connection import get_database
from dev_agent.database.repositories.users import UsersRepository
from dev_agent.database.models.user import UserInDB

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_database),
):
    """
    Dependência FastAPI — valida o JWT e devolve o utilizador actual.
    Usa-se nas rotas protegidas: async def route(user = Depends(get_current_user))
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    users_repo = UsersRepository(db)
    user = await users_repo.find_by_id(payload["sub"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizador não encontrado",
        )

    return user


async def resolve_user_for_oauth(
    state: Optional[str] = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        optional_security
    ),
    db=Depends(get_database),
) -> UserInDB:
    """OAuth callback: Bearer (frontend) ou parâmetro state (browser)."""
    return await resolve_user_for_oauth_from_params(state, credentials, db)


async def resolve_user_for_oauth_from_params(
    state: Optional[str],
    credentials: Optional[HTTPAuthorizationCredentials],
    db,
) -> UserInDB:
    user_id: Optional[str] = None

    if credentials:
        payload = decode_token(credentials.credentials)
        if payload:
            user_id = payload.get("sub")

    if not user_id and state:
        user_id = verify_oauth_state(state)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    users_repo = UsersRepository(db)
    user = await users_repo.find_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilizador não encontrado",
        )

    return user
