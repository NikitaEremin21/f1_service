from aiogram import Bot
from django.conf import settings
import asyncio
from asgiref.sync import async_to_sync
from loguru import logger


class TelegramService:
    """
    Сервис для отправки сообщений в телеграм
    """
    _instance = None
    _bot = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._bot is None:
            token = settings.BOT_TOKEN
            if not token:
                raise ValueError("Токен Telegram-бота не задан в настройках")
            self._bot = Bot(token=token)
            logger.info("✅ Создан экземпляр Telegram-бота для уведомлений")

    def send_message(self, telegram_id, message):
        """
        Отправляет сообщение пользователю
        """
        try:
            async_to_sync(self._bot.send_message)(
                chat_id=telegram_id,
                text=message,
                parse_mode="HTML"
            )

            return True
        
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {telegram_id}: {e}")
            return False


telegram_bot = TelegramService()