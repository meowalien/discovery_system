import redis.asyncio as redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB
from logger.logger import get_logger

# Create an asynchronous Redis client
_redis_client = None
_logger = get_logger(__name__)

def redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    return _redis_client


async def ping_redis():
    """
    Ping the Redis server to verify the connection.
    """
    try:
        await _redis_client.ping()
        _logger.info("Redis connection successful")
    except redis.ConnectionError:
        _logger.info("Redis connection failed")

def new_redis_key(*keys: str) -> str:
    """
    Generate a new Redis key by concatenating the provided keys with a colon.
    Accepts an arbitrary number of string arguments.
    """
    return ":".join(keys)


# key enum
class RedisKey:
    """
    Enum-like class to define Redis keys.
    """
    SESSION = "session"
