from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional
from datetime import datetime, timedelta
import random
import string

from dev_agent.database.models.user import UserInDB


class UsersRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.users

    async def create(self, email: str, hashed_password: str) -> UserInDB:
        """Create a new user with a verification code."""
        code = self._generate_verification_code()
        expires = datetime.utcnow() + timedelta(minutes=15)
        
        doc = {
            "email": email,
            "hashed_password": hashed_password,
            "verified": False,
            "verification_code": code,
            "verification_code_expires": expires,
            "github_token": None,
            "github_username": None,
            "google_token": None,
            "google_refresh_token": None,
            "created_at": datetime.utcnow(),
            "last_login": None,
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return UserInDB(**doc)

    async def find_by_email(self, email: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"email": email})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return UserInDB(**doc)

    async def find_by_id(self, user_id: str) -> Optional[UserInDB]:
        doc = await self.collection.find_one({"_id": ObjectId(user_id)})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return UserInDB(**doc)

    async def verify_email(self, email: str, code: str) -> bool:
        """Verify the code and activate the account. Return True if successful."""
        user = await self.find_by_email(email)
        if not user:
            return False
        if user.verification_code != code:
            return False
        if user.verification_code_expires < datetime.utcnow():
            return False  
        
        await self.collection.update_one(
            {"email": email},
            {"$set": {"verified": True, "verification_code": None}}
        )
        return True

    async def update_github_token(self, user_id: str, token: str, username: str) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"github_token": token, "github_username": username}}
        )

    async def update_google_token(self, user_id: str, token: str, refresh_token: str) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"google_token": token, "google_refresh_token": refresh_token}}
        )

    async def update_last_login(self, user_id: str) -> None:
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
        )

    async def remove_github_token(self, user_id: str) -> None:
        """Remove GitHub token and username for the user."""
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"github_token": None, "github_username": None}}
        )

    async def remove_google_token(self, user_id: str) -> None:
        """Remove Google token and refresh_token for the user."""
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"google_token": None, "google_refresh_token": None}}
        )

    def _generate_verification_code(self) -> str:
        """Gera um código de 6 dígitos."""
        return "".join(random.choices(string.digits, k=6))