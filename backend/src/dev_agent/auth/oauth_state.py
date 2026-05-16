from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError

from dev_agent.core.config import get_settings

OAUTH_STATE_PURPOSE = "oauth_link"
OAUTH_STATE_MINUTES = 15


def create_oauth_state(user_id: str) -> str:
    """Token curto incluído no parâmetro state do OAuth (voltar sem Bearer)."""
    settings = get_settings()
    payload = {
        "sub": user_id,
        "purpose": OAUTH_STATE_PURPOSE,
        "exp": datetime.utcnow() + timedelta(minutes=OAUTH_STATE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def verify_oauth_state(state: str) -> Optional[str]:
    """Devolve user_id se o state for válido."""
    settings = get_settings()
    try:
        payload = jwt.decode(
            state,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("purpose") != OAUTH_STATE_PURPOSE:
            return None
        return payload.get("sub")
    except JWTError:
        return None
