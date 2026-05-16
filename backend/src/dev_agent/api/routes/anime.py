from fastapi import APIRouter, Depends
from pydantic import BaseModel

from dev_agent.agents.anime_agent import AnimeAgent
from dev_agent.database.connection import get_database
from dev_agent.database.repositories.emails import AnimeSuggestionsRepository
from dev_agent.api.dependencies import get_current_user

router = APIRouter(prefix="/anime", tags=["easter-egg"])


class SuggestionRequest(BaseModel):
    anime_title: str
    reason: str


@router.get("/recommend")
async def get_anime_recommendation(current_user=Depends(get_current_user)):
    """Easter egg — recomendação de anime baseada no perfil do dev."""
    agent = AnimeAgent(user_id=current_user.id)
    result = await agent.run("recommenda anime para mim")
    return result.data


@router.post("/suggest")
async def suggest_anime(body: SuggestionRequest, db=Depends(get_database),
                        current_user=Depends(get_current_user)):
    """
    O utilizador sugere um anime.
    O agente critica e, se aprovado, guarda para a comunidade.
    """
    agent = AnimeAgent(user_id=current_user.id)
    critique = await agent.critique_suggestion(body.anime_title, body.reason)
    
    # Guardar sugestão no MongoDB
    repo = AnimeSuggestionsRepository(db)
    await repo.create(
        anime_title=body.anime_title,
        suggested_by_user_id=current_user.id,
        suggested_by_email=current_user.email,
        reason=body.reason,
        agent_critique=critique.get("critique", ""),
        approved=critique.get("approved", False),
        tags=critique.get("tags", []),
    )
    
    return {
        "critique": critique["critique"],
        "approved": critique["approved"],
        "score": critique["score"],
    }