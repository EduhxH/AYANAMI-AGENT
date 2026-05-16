from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserPreferencesInDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    display_name: str = ""
    avatar_url: str = ""
    agent_instructions: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class UserPreferencesPublic(BaseModel):
    user_id: str
    display_name: str
    avatar_url: str
    agent_instructions: str
    created_at: datetime
    updated_at: datetime


class UserPreferencesUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    agent_instructions: Optional[str] = None
