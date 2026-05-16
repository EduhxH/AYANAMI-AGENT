from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class UserInDB(BaseModel):
    """It represents a user as stored in MongoDB."""
    id: Optional[str] = Field(default=None, alias="_id")
    email: EmailStr
    hashed_password: str
    verified: bool = False
    verification_code: Optional[str] = None
    verification_code_expires: Optional[datetime] = None
    
    github_token: Optional[str] = None
    github_username: Optional[str] = None
    google_token: Optional[str] = None
    google_refresh_token: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True 


class UserPublic(BaseModel):
    """What we return to the frontend — WITHOUT the password and tokens."""
    id: str
    email: str
    verified: bool
    github_username: Optional[str] = None
    has_github: bool = False
    has_google: bool = False
    created_at: datetime