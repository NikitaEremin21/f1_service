import redis.asyncio as redis
from django.conf import settings
import asyncio
from loguru import logger


class RedisClient:
    def __init__(self):
        self._client = None
        self._loop = None

    async def _get_client(self):
        current_loop = asyncio.get_running_loop()

        if self._client is None:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
            self._loop = current_loop
            logger.success("Redis клиент создан")
            return self._client

        if self._loop is not current_loop:
            logger.info("Обнаружен новый event loop. Пересоздаем Redis клиент.")
            try:
                await self._client.aclose()
            except Exception as e:
                logger.exception(f"Ошибка при закрытии старого Redis клиента: {e}")

            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
            self._loop = current_loop
            logger.success("Redis клиент обновлён")

        return self._client

    async def get(self, key: str):
        client = await self._get_client()
        return await client.get(key)

    async def set(self, key: str, value: str, ttl: int):
        client = await self._get_client()
        return await client.setex(key, ttl, value)

    async def delete(self, key: str):
        client = await self._get_client()
        return await client.delete(key)


redis_client = RedisClient()