import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from tg_bot.config_data import config
from tg_bot.handlers import router


async def main():
    """Запуск бота."""
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    logger.success('✅ Бот запущен!')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
