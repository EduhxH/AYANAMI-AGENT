from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr

from dev_agent.auth.service import AuthService
from dev_agent.auth.oauth_github import GitHubOAuth
from dev_agent.auth.oauth_google import GoogleOAuth
from dev_agent.auth.oauth_state import create_oauth_state
from dev_agent.core.config import get_settings
from dev_agent.database.connection import get_database
from dev_agent.database.repositories.users import UsersRepository
from dev_agent.database.models.user import UserPublic
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from dev_agent.api.dependencies import (
    get_current_user,
    resolve_user_for_oauth_from_params,
)

optional_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Schemas de request/response ──────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class VerifyRequest(BaseModel):
    email: EmailStr
    code: str


def _wants_browser_redirect(request: Request) -> bool:
    """Redirect do Google/GitHub no browser (sem header Authorization)."""
    if request.headers.get("authorization"):
        return False
    accept = request.headers.get("accept", "")
    return "text/html" in accept or "*/*" in accept


def _oauth_success_redirect(provider: str) -> RedirectResponse:
    settings = get_settings()
    url = (
        f"{settings.frontend_url}/dashboard/settings"
        f"?oauth={provider}&status=success"
    )
    return RedirectResponse(url=url, status_code=302)


def _oauth_error_redirect(provider: str, detail: str) -> RedirectResponse:
    settings = get_settings()
    from urllib.parse import quote

    url = (
        f"{settings.frontend_url}/dashboard/settings"
        f"?oauth={provider}&status=error&message={quote(detail)}"
    )
    return RedirectResponse(url=url, status_code=302)


# ── Rotas ────────────────────────────────────────────────────────

@router.post("/register")
async def register(body: RegisterRequest, db=Depends(get_database)):
    users_repo = UsersRepository(db)
    service = AuthService(users_repo)

    try:
        return await service.register(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify")
async def verify_email(body: VerifyRequest, db=Depends(get_database)):
    users_repo = UsersRepository(db)
    service = AuthService(users_repo)

    try:
        return await service.verify_email(body.email, body.code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
async def login(body: LoginRequest, db=Depends(get_database)):
    users_repo = UsersRepository(db)
    service = AuthService(users_repo)

    try:
        return await service.login(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/me", response_model=UserPublic)
async def me(current_user=Depends(get_current_user)):
    """Rota protegida — devolve o perfil do utilizador autenticado."""
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        verified=current_user.verified,
        github_username=current_user.github_username,
        has_github=current_user.github_token is not None,
        has_google=current_user.google_token is not None,
        created_at=current_user.created_at,
    )


# ── OAuth GitHub ─────────────────────────────────────────────────

@router.get("/github")
async def github_login(
    request: Request,
    current_user=Depends(get_current_user),
):
    """Devolve o URL para onde o frontend redireciona o utilizador."""
    oauth = GitHubOAuth()
    state = create_oauth_state(current_user.id)
    return {"url": oauth.get_authorization_url(state=state, request=request)}


@router.get("/callback/github")
async def github_callback(
    request: Request,
    code: str,
    state: str | None = None,
    db=Depends(get_database),
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
):
    """
    GitHub redireciona aqui após o utilizador autorizar.
    Aceita JWT (frontend) ou state OAuth (redirect directo no browser).
    """
    oauth = GitHubOAuth()
    browser = _wants_browser_redirect(request)

    try:
        current_user = await resolve_user_for_oauth_from_params(
            state, credentials, db
        )
        token = await oauth.exchange_code_for_token(code)
        user_info = await oauth.get_user_info(token)

        users_repo = UsersRepository(db)
        await users_repo.update_github_token(
            current_user.id,
            token,
            user_info["login"],
        )

        if browser:
            return _oauth_success_redirect("github")

        return {
            "message": "GitHub ligado com sucesso",
            "username": user_info["login"],
        }
    except HTTPException as e:
        if browser:
            detail = e.detail if isinstance(e.detail, str) else "Not authenticated"
            return _oauth_error_redirect("github", detail)
        raise
    except ValueError as e:
        if browser:
            return _oauth_error_redirect("github", str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        if browser:
            return _oauth_error_redirect("github", str(e))
        raise HTTPException(status_code=400, detail=str(e))


# ── OAuth Google ─────────────────────────────────────────────────

@router.get("/google")
async def google_login(
    request: Request,
    current_user=Depends(get_current_user),
):
    oauth = GoogleOAuth()
    state = create_oauth_state(current_user.id)
    return {"url": oauth.get_authorization_url(state=state, request=request)}


@router.get("/callback/google")
async def google_callback(
    request: Request,
    code: str,
    state: str | None = None,
    db=Depends(get_database),
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
):
    oauth = GoogleOAuth()
    browser = _wants_browser_redirect(request)

    try:
        current_user = await resolve_user_for_oauth_from_params(
            state, credentials, db
        )
        tokens = await oauth.exchange_code_for_token(code)

        if "error" in tokens:
            msg = tokens.get("error_description", tokens["error"])
            if browser:
                return _oauth_error_redirect("google", msg)
            raise HTTPException(status_code=400, detail=msg)

        access = tokens.get("access_token")
        if not access:
            msg = "Resposta Google sem access_token"
            if browser:
                return _oauth_error_redirect("google", msg)
            raise HTTPException(status_code=400, detail=msg)

        users_repo = UsersRepository(db)
        await users_repo.update_google_token(
            current_user.id,
            access,
            tokens.get("refresh_token", ""),
        )

        if browser:
            return _oauth_success_redirect("google")

        return {"message": "Gmail ligado com sucesso"}
    except HTTPException as e:
        if browser:
            detail = e.detail if isinstance(e.detail, str) else "Erro OAuth"
            return _oauth_error_redirect("google", detail)
        raise
    except Exception as e:
        if browser:
            return _oauth_error_redirect("google", str(e))
        raise HTTPException(status_code=400, detail=str(e))


# ── Disconnect/Revoke ────────────────────────────────────────────

@router.post("/disconnect/github")
async def disconnect_github(
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    """Remove GitHub token and username for the current user."""
    users_repo = UsersRepository(db)
    await users_repo.remove_github_token(current_user.id)
    return {"message": "GitHub desconectado com sucesso"}


@router.post("/disconnect/google")
async def disconnect_google(
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    """Remove Google token for the current user."""
    users_repo = UsersRepository(db)
    await users_repo.remove_google_token(current_user.id)
    return {"message": "Gmail desconectado com sucesso"}
