import logging

from pymongo import DESCENDING, AsyncMongoClient

from app.config import MONGODB_DB_NAME, MONGODB_URI

logger = logging.getLogger(__name__)

_client: AsyncMongoClient | None = None


def get_db():
    global _client
    if _client is None:
        _client = AsyncMongoClient(
            MONGODB_URI,
            tz_aware=True,
            serverSelectionTimeoutMS=3000,
        )
    return _client[MONGODB_DB_NAME]


def claims_collection():
    return get_db()["claims"]


async def init_db() -> None:
    claims = claims_collection()
    await claims.create_index("claim_key", unique=True)
    await claims.create_index([("last_analyzed_at", DESCENDING)])
    logger.info("MongoDB indexes ready")


async def close_db() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None