from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class EmailRecordInDB(BaseModel):
    """History of a processed email."""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    gmail_message_id: str
    from_address: str
    subject: str
    classification: str      # "urgent", "newsletter", "support", etc.
    summary: str
    reply_sent: bool = False
    reply_content: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class AnimeSuggestionInDB(BaseModel):
    """Anime suggestion from the community — easter egg."""
    id: Optional[str] = Field(default=None, alias="_id")
    anime_title: str
    suggested_by_user_id: str
    suggested_by_email: str
    reason: str              # why this anime for devs
    agent_critique: str      # what the agent thought of the suggestion
    approved: bool = False
    tags: List[str] = []     # ["python", "backend", "systems"]
    times_recommended: int = 0
    community_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True