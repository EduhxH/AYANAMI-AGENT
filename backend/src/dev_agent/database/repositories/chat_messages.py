from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from datetime import datetime

from dev_agent.database.models.chat_message import ChatMessage


class ChatMessagesRepository:
    """Repositório para gerir operações de leitura e escrita de ChatMessage em MongoDB."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.chat_messages

    async def save_message(
        self,
        user_id: str,
        role: str,
        content: str,
        agent_used: Optional[List[str]] = None,
    ) -> ChatMessage:
        """Guarda uma nova mensagem na base de dados."""
        doc = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
            "agent_used": agent_used,
        }
        result = await self.collection.insert_one(doc)
        doc["_id"] = str(result.inserted_id)
        return ChatMessage(**doc)

    async def get_history(self, user_id: str, limit: int = 10) -> List[dict]:
        """Recupera as últimas mensagens ordenadas por timestamp de forma decrescente."""
        cursor = self.collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        return docs
