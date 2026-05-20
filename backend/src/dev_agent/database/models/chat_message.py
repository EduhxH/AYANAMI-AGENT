from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    """Representa uma mensagem do chat de conversação persistida em MongoDB."""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_used: Optional[List[str]] = None

    class Config:
        populate_by_name = True
