import asyncio
from contextlib import suppress

from aiohttp import ClientSession, ClientTimeout
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings
from services.http_client import http_client
from tg_bot.handlers import router


async def monitor_service(bot):
    if not settings.SERVICE_HEARTBEAT_URL:
        logger.warning("SERVICE_HEARTBEAT_URL is not configured; external monitoring is disabled")

    timeout = ClientTimeout(total=10)
    async with ClientSession(timeout=timeout) as session:
        while True:
            try:
                await bot.get_me()

                async with session.get(settings.MONITORING_BACKEND_HEALTH_URL) as response:
                    if response.status != 200:
                        raise RuntimeError(
                            f"Backend health check returned HTTP {response.status}"
                        )

                if settings.SERVICE_HEARTBEAT_URL:
                    async with session.get(settings.SERVICE_HEARTBEAT_URL) as response:
                        response.raise_for_status()
                    logger.debug("Service health check sent")
            except Exception:
                logger.exception("Service health check failed")

            await asyncio.sleep(settings.SERVICE_HEARTBEAT_INTERVAL_SECONDS)


async def main():
    """Запуск бота."""
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    logger.success('✅ Бот запущен!')
    monitor_task = asyncio.create_task(monitor_service(bot))

    try:
        await dp.start_polling(bot)
    finally:
        monitor_task.cancel()
        with suppress(asyncio.CancelledError):
            await monitor_task
        await http_client.close()
        await bot.session.close()
        logger.success('✅ Бот остановлен!')

if __name__ == "__main__":
    asyncio.run(main())
    
