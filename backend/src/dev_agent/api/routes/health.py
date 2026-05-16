from fastapi import APIRouter
from dev_agent.database.connection import get_database
from fastapi import Depends

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(db=Depends(get_database)):
    """Verifica se o servidor e o MongoDB estão a funcionar."""
    try:
        await db.command("ping")
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "ok", "database": "disconnected"}