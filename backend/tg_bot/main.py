import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from services.http_client import http_client
from tg_bot.config_data import config
from tg_bot.handlers import router


async def main():
    """Запуск бота."""
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    logger.success('✅ Бот запущен!')

    try:
        await dp.start_polling(bot)
    finally:
        await http_client.close()
        await bot.session.close()
        logger.success('✅ Бот остановлен!')

if __name__ == "__main__":
    asyncio.run(main())
    
