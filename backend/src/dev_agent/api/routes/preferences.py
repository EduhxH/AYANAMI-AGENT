from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from dev_agent.api.dependencies import get_current_user
from dev_agent.database.connection import get_database
from dev_agent.database.models.user_preferences import (
    UserPreferencesPublic,
    UserPreferencesUpdate,
)
from dev_agent.database.repositories.user_preferences import UserPreferencesRepository
from dev_agent.preferences.storage import save_avatar_file

router = APIRouter(prefix="/api/preferences", tags=["preferences"])


@router.get("", response_model=UserPreferencesPublic)
async def get_preferences(
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    repo = UserPreferencesRepository(db)
    default_name = current_user.email.split("@")[0]
    return await repo.get_or_create(current_user.id, default_display_name=default_name)


@router.put("", response_model=UserPreferencesPublic)
async def update_preferences(
    body: UserPreferencesUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    repo = UserPreferencesRepository(db)
    try:
        return await repo.update(current_user.id, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/avatar", response_model=UserPreferencesPublic)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
    db=Depends(get_database),
):
    repo = UserPreferencesRepository(db)
    try:
        avatar_url = await save_avatar_file(current_user.id, file)
        return await repo.set_avatar_url(current_user.id, avatar_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
