import asyncio
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from django.conf import settings
from tg_bot.handlers import router


async def main():
    """Запуск бота."""
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    logger.success('✅ Бот запущен!')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
