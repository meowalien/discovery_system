# File: redis_session_manager.py
import asyncio
from redis.asyncio import Redis
from logger.logger import get_logger

_logger = get_logger(__name__)

class RedisSessionManager:
    def __init__(self, redis: Redis, hostname: str, ttl: int = 30, refresh_interval: int = 20):
        self.redis = redis
        self.key = f"telegram_reader_sessions:{hostname}"
        self.ttl = ttl
        self.refresh_interval = refresh_interval
        self._task = None

    async def init(self):
        # Initialize an empty set with TTL
        await self.redis.delete(self.key)
        # hack: create then remove placeholder to ensure empty set
        await self.redis.sadd(self.key, "__init__")
        await self.redis.expire(self.key, self.ttl)

    async def add_session(self, session_id: str):
        # add a session to the set and refresh TTL
        await self.redis.sadd(self.key, session_id)
        await self.redis.expire(self.key, self.ttl)

    async def remove_session(self, session_id: str):
        # remove a session from the set
        await self.redis.srem(self.key, session_id)

    async def clear_sessions(self):
        # clear all sessions by reinitializing
        await self.init()

    async def _refresh_loop(self, manager):
        while True:
            await asyncio.sleep(self.refresh_interval)
            ok = await self.redis.expire(self.key, self.ttl)
            if not ok:
                _logger.info(f"Key '{self.key}' missing: shutting down all clients and reinitializing set.")
                try:
                    await manager.shutdown_all()
                except Exception as e:
                    _logger.error(f"Error during shutdown_all: {e}")
                await self.clear_sessions()

    async def start(self, manager):
        # initial setup and spawn TTL refresher
        await self.init()
        self._task = asyncio.create_task(self._refresh_loop(manager))

    async def cleanup(self):
        # cancel refresher, delete key and close connection
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        await self.redis.delete(self.key)
        await self.redis.close()
