import redis.asyncio as redis
import json
import os
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

class Cache:
    def __init__(self):
        self.redis = None
        self._connected = False

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await redis.from_url(REDIS_URL, decode_responses=True)
            await self.redis.ping()
            self._connected = True
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False

    async def get(self, key: str):
        """Get a value from cache"""
        if not self._connected or not self.redis:
            return None
        try:
            data = await self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: dict, ttl=60):
        """Set a value in cache with TTL"""
        if not self._connected or not self.redis:
            return
        try:
            await self.redis.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Redis set error: {e}")

    async def delete(self, key: str):
        """Delete a value from cache"""
        if not self._connected or not self.redis:
            return
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete error: {e}")

# Create a cache instance
cache = Cache()
