from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime


class EmailsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.emails_processed

    async def create(self, user_id: str, gmail_message_id: str, from_address: str,
                     subject: str, classification: str, summary: str) -> dict:
        doc = {
            "user_id": user_id,
            "gmail_message_id": gmail_message_id,
            "from_address": from_address,
            "subject": subject,
            "classification": classification,
            "summary": summary,
            "reply_sent": False,
            "processed_at": datetime.utcnow(),
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    async def find_by_user(self, user_id: str, limit: int = 20) -> List[dict]:
        cursor = self.collection.find({"user_id": user_id}).sort("processed_at", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results


class AnimeSuggestionsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.anime_suggestions

    async def create(self, anime_title: str, suggested_by_user_id: str,
                     suggested_by_email: str, reason: str, agent_critique: str,
                     approved: bool, tags: List[str]) -> dict:
        doc = {
            "anime_title": anime_title,
            "suggested_by_user_id": suggested_by_user_id,
            "suggested_by_email": suggested_by_email,
            "reason": reason,
            "agent_critique": agent_critique,
            "approved": approved,
            "tags": tags,
            "times_recommended": 0,
            "community_score": 0.0,
            "created_at": datetime.utcnow(),
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return doc

    async def find_approved(self, limit: int = 20) -> List[dict]:
        cursor = self.collection.find({"approved": True}).sort("community_score", -1).limit(limit)
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results