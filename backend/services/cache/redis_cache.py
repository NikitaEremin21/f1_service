import redis.asyncio as redis_async
import redis as redis_sync
from django.conf import settings
import asyncio
from loguru import logger
import weakref

_sync_client = None

def get_sync_client():
    """
    Возвращает синхронный Redis-клиент
    """
    global _sync_client
    if _sync_client is None:
        _sync_client = redis_sync.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        logger.success("Sync Redis клиент создан")
    return _sync_client

def sync_get(key: str):
    return get_sync_client().get(key)

def sync_set(key: str, value: str, ttl: int):
    return get_sync_client().setex(key, ttl, value)

def sync_delete(key: str):
    return get_sync_client().delete(key)



_async_clients = weakref.WeakKeyDictionary()

async def get_async_client():
    """
    Возвращает асинхронный Redis-клиент
    """
    current_loop = asyncio.get_running_loop()

    client = _async_clients.get(current_loop)
    if client is not None:
        return client

    client = redis_async.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )
    _async_clients[current_loop] = client
    logger.success(f"Async Redis клиент создан для event loop {id(current_loop)}")
    return client


async def async_get(key: str):
    client = await get_async_client()
    return await client.get(key)

async def async_set(key: str, value: str, ttl: int):
    client = await get_async_client()
    return await client.setex(key, ttl, value)

async def async_delete(key: str):
    client = await get_async_client()
    return await client.delete(key)


async def close_async_client_for_current_loop():
    loop = asyncio.get_running_loop()
    client = _async_clients.pop(loop, None)
    if client is None:
        return
    try:
        await client.aclose()
        logger.success(f"Async Redis клиент для loop {id(loop)} закрыт")
    except RuntimeError as e:
        logger.error(f"RuntimeError при закрытии async Redis клиента: {e}")
    except Exception as e:
        logger.exception(f"Ошибка при закрытии async Redis клиента: {e}")


class _BackwardCompatAsyncClient:
    async def get(self, key: str):
        return await async_get(key)

    async def set(self, key: str, value: str, ttl: int):
        return await async_set(key, value, ttl)

    async def delete(self, key: str):
        return await async_delete(key)


redis_client = _BackwardCompatAsyncClient()
