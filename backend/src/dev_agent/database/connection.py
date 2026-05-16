from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dev_agent.core.config import get_settings

# Variável global — uma única conexão para toda a app
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_to_mongodb() -> None:
    """this is called on startup of the FastAPI app."""
    global _client, _db
    settings = get_settings()
    
    _client = AsyncIOMotorClient(settings.mongodb_url)
    _db = _client[settings.database_name]
    
    # Cria índices necessários
    await _db.users.create_index("email", unique=True)
    await _db.users.create_index("verification_code")
    await _db.analyses.create_index("user_id")
    await _db.anime_suggestions.create_index("approved")
    
    print("MongoDB connected")


async def close_mongodb_connection() -> None:
    """this is called on shutdown of the FastAPI app."""
    global _client
    if _client:
        _client.close()
        print("MongoDB disconnected")


def get_database() -> AsyncIOMotorDatabase:
    """Use the FastAPI dependencies to obtain the DB."""
    if _db is None:
        raise RuntimeError("MongoDB is not connected. Call connect_to_mongodb() first.")
    return _db