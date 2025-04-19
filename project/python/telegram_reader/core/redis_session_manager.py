# File: redis_session_manager.py
import asyncio

from redis.asyncio import Redis

from data_source.redis_client import new_redis_key, RedisKey
from logger.logger import get_logger

_logger = get_logger(__name__)


class RedisSessionManager:
    def __init__(self, redis: Redis, hostname: str, ttl: int = 30, refresh_interval: int = 20):
        self.redis = redis
        self.telegram_readers_key = new_redis_key(RedisKey.TELEGRAM_READERS)
        self.telegram_reader_sessions_key = new_redis_key(RedisKey.TELEGRAM_READER_SESSIONS, hostname)
        self.ttl = ttl
        self.refresh_interval = refresh_interval
        self._task = None

    async def init(self):
        # append hostname to the self.telegram_readers_key if not already present in atomic operation
        # this is a set, so it will not add duplicates
        await self.redis.sadd(self.telegram_readers_key, self.telegram_reader_sessions_key)

        # Initialize an empty set with TTL
        await self.redis.delete(self.telegram_reader_sessions_key)
        # hack: create then remove placeholder to ensure empty set
        await self.redis.sadd(self.telegram_reader_sessions_key, "__init__")
        await self.redis.expire(self.telegram_reader_sessions_key, self.ttl)

    async def add_session(self, session_id: str):
        # add a session to the set and refresh TTL
        await self.redis.sadd(self.telegram_reader_sessions_key, session_id)
        await self.redis.expire(self.telegram_reader_sessions_key, self.ttl)

    async def remove_session(self, session_id: str):
        # remove a session from the set
        await self.redis.srem(self.telegram_reader_sessions_key, session_id)

    async def clear_sessions(self):
        # clear all sessions by reinitializing
        await self.init()

    async def _refresh_loop(self, manager):
        while True:
            await asyncio.sleep(self.refresh_interval)
            ok = await self.redis.expire(self.telegram_reader_sessions_key, self.ttl)
            if not ok:
                _logger.info(
                    f"Key '{self.telegram_reader_sessions_key}' missing: shutting down all clients and reinitializing set.")
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
        await self.redis.delete(self.telegram_reader_sessions_key)
        # delete the reader node key in self.telegram_readers_key
        await self.redis.srem(self.telegram_readers_key, self.telegram_reader_sessions_key)

        await self.redis.close()
