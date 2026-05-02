import redis.asyncio as redis
from django.conf import settings


class RedisClient:
    def __init__(self):
        self._client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    async def get(self, key: str):
        return await self._client.get(key)

    async def set(self, key: str, value: str, ttl: int):
        return await self._client.setex(key, ttl, value)

    async def delete(self, key: str):
        return await self._client.delete(key)


redis_client = RedisClient()