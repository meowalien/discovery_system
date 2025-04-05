# app/redis_client.py
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