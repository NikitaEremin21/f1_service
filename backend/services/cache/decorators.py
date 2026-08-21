import json
import functools
from django.conf import settings
from services.cache.redis_cache import async_get, async_set


def async_cache(prefix: str, ttl: int = None):
    """
    Redis cache декоратор
    """

    def decorator(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            key_parts = [prefix]
            for arg in args:
                if isinstance(arg, str):
                    key_parts.append(arg.replace(' ', '_').replace("'", ""))
                elif isinstance(arg, int):
                    key_parts.append(str(arg))
                else:
                    key_parts.append(str(arg))

            key_raw = ":".join(key_parts)

            cached = await async_get(key_raw)

            if cached is not None:
                return json.loads(cached)

            result = await func(*args, **kwargs)

            # НЕ кэшируем пустые/ошибочные ответы
            if result is not None and result != [] and result != {}:
                await async_set(
                    key_raw,
                    json.dumps(result, default=str),
                    ttl or settings.REDIS_TTL
                )

            return result

        return wrapper

    return decorator