from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

from dev_agent.core.config import get_settings


def create_access_token(user_id: str, email: str) -> str:
    """Create a JWT that the frontend will store and send with each request."""
    settings = get_settings()
    
    payload = {
        "sub": user_id,          
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes),
        "iat": datetime.utcnow(), 
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    """Validate the token and return the payload. Returns None if invalid."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None