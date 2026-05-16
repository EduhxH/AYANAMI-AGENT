from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AnalysisInDB(BaseModel):
    """History of a repository analysis."""
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    repo_url: str
    repo_name: str
    summary: str
    issues_found: List[str] = []
    pr_created: bool = False
    pr_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True