import redis.asyncio as redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB

# Create an asynchronous Redis client
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

async def ping_redis():
    """
    Ping the Redis server to verify the connection.
    """
    try:
        await redis_client.ping()
        print("Redis connection successful")
    except redis.ConnectionError:
        print("Redis connection failed")

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
