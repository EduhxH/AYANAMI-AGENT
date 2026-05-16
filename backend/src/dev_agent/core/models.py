from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class AgentType(str, Enum):
    GITHUB = "github"
    EMAIL = "email"
    ANIME = "anime"
    GENERAL = "general"


class TaskRequest(BaseModel):
    query: str
    user_id: str
    agents: Optional[List[AgentType]] = None 


class AgentResult(BaseModel):
    agent: AgentType
    success: bool
    data: dict
    error: Optional[str] = None


class OrchestratorResult(BaseModel):
    query: str
    results: List[AgentResult]
    summary: str  