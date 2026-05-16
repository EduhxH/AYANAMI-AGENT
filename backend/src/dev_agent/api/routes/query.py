from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List

from dev_agent.core.models import TaskRequest, AgentType
from dev_agent.orchestrator.orchestrator import Orchestrator
from dev_agent.api.dependencies import get_current_user
from dev_agent.auth.google_tokens import ensure_fresh_google_token
from dev_agent.database.connection import get_database
from dev_agent.database.repositories.users import UsersRepository

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    query: str
    agents: Optional[List[AgentType]] = None


@router.post("/")
async def handle_query(
    body: QueryRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    users_repo = UsersRepository(db)

    async def refresh_google() -> str:
        user = await users_repo.find_by_id(current_user.id)
        if not user:
            return ""
        refreshed = await ensure_fresh_google_token(user, users_repo)
        return refreshed or user.google_token or ""

    user_data = {
        "user_id": current_user.id,
        "github_token": current_user.github_token,
        "github_username": current_user.github_username,
        "google_token": current_user.google_token,
    }

    orchestrator = Orchestrator(on_google_token_refresh=refresh_google)
    task = TaskRequest(
        query=body.query,
        user_id=current_user.id,
        agents=body.agents,
    )

    return await orchestrator.handle(task, user_data)
