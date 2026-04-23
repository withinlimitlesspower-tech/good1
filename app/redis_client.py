import json
import redis.asyncio as redis
from typing import Optional, Any
from app.config import get_settings

settings = get_settings()

class RedisClient:
    def __init__(self):
        self.client = None

    async def connect(self):
        self.client = redis.from_url(settings.redis_url, decode_responses=True)

    async def close(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            return None
        return await self.client.get(key)

    async def set(self, key: str, value: Any, expire: int = 300):
        if not self.client:
            return
        await self.client.set(key, json.dumps(value), ex=expire)

    async def delete(self, key: str):
        if not self.client:
            return
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        if not self.client:
            return False
        return await self.client.exists(key) > 0

redis_client = RedisClient()
