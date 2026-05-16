from datetime import datetime
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from dev_agent.database.models.user_preferences import (
    UserPreferencesInDB,
    UserPreferencesPublic,
    UserPreferencesUpdate,
)


class UserPreferencesRepository:
    collection_name = "user_preferences"

    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db[self.collection_name]

    async def ensure_indexes(self) -> None:
        await self.collection.create_index("user_id", unique=True)

    def _to_public(self, doc: dict) -> UserPreferencesPublic:
        return UserPreferencesPublic(
            user_id=doc["user_id"],
            display_name=doc.get("display_name", ""),
            avatar_url=doc.get("avatar_url", ""),
            agent_instructions=doc.get("agent_instructions", ""),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    async def find_by_user_id(self, user_id: str) -> Optional[UserPreferencesInDB]:
        doc = await self.collection.find_one({"user_id": user_id})
        if not doc:
            return None
        doc["_id"] = str(doc["_id"])
        return UserPreferencesInDB(**doc)

    async def get_or_create(
        self, user_id: str, default_display_name: str = ""
    ) -> UserPreferencesPublic:
        doc = await self.collection.find_one({"user_id": user_id})
        if doc:
            return self._to_public(doc)

        now = datetime.utcnow()
        doc = {
            "user_id": user_id,
            "display_name": default_display_name,
            "avatar_url": "",
            "agent_instructions": "",
            "created_at": now,
            "updated_at": now,
        }
        await self.collection.insert_one(doc)
        return self._to_public(doc)

    async def update(
        self, user_id: str, payload: UserPreferencesUpdate
    ) -> UserPreferencesPublic:
        await self.get_or_create(user_id)

        updates = {
            k: v
            for k, v in payload.model_dump(exclude_unset=True).items()
            if v is not None
        }
        updates["updated_at"] = datetime.utcnow()

        await self.collection.update_one(
            {"user_id": user_id},
            {"$set": updates},
        )

        doc = await self.collection.find_one({"user_id": user_id})
        return self._to_public(doc)

    async def set_avatar_url(self, user_id: str, avatar_url: str) -> UserPreferencesPublic:
        return await self.update(
            user_id,
            UserPreferencesUpdate(avatar_url=avatar_url),
        )
