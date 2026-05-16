from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from bson import ObjectId
from datetime import datetime

from dev_agent.database.models.analysis import AnalysisInDB


class AnalysesRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.analyses

    async def create(self, user_id: str, repo_url: str, repo_name: str,
                     summary: str, issues: List[str], pr_url: str = None) -> AnalysisInDB:
        doc = {
            "user_id": user_id,
            "repo_url": repo_url,
            "repo_name": repo_name,
            "summary": summary,
            "issues_found": issues,
            "pr_created": pr_url is not None,
            "pr_url": pr_url,
            "created_at": datetime.utcnow(),
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return AnalysisInDB(**doc)

    async def find_by_user(self, user_id: str, limit: int = 20) -> List[AnalysisInDB]:
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)
        
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(AnalysisInDB(**doc))
        return results