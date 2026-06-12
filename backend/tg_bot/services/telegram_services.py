from aiogram import Bot
from django.conf import settings
import asyncio
from asgiref.sync import async_to_sync
from loguru import logger


def send_message(telegram_id, message):
    try:
        bot = Bot(token=settings.BOT_TOKEN)

        async_to_sync(bot.send_message)(
            chat_id=telegram_id,
            text=message,
            parse_mode="HTML"
        )

        async_to_sync(bot.session.close)()

        return True
    
    except Exception as e:
        logger.error(f"Ошибка отправки {telegram_id}: {e}")
        return False