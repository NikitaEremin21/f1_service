from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from django.conf import settings
import asyncio
from asgiref.sync import async_to_sync
from loguru import logger


class TelegramService:
    """
    Сервис для отправки сообщений в телеграм
    """
    def __init__(self):
        self.token = settings.BOT_TOKEN
        if not self.token:
            raise ValueError("Токен Telegram-бота не задан в настройках")


    def send_messages(self, notifications):
        """
        Отправляет сообщения пользователям
        """
        return async_to_sync(self._send_messages)(notifications)

    async def _send_messages(self, notifications):
        """
        Асинхронная отправка сообщений пользователям
        """
        bot = Bot(token=self.token)
        try:
            results = []

            for telegram_id, message in notifications:
                success = await self._send_message(
                    bot,
                    telegram_id,
                    message
                )
                results.append(success)

            return results

        finally:
            await bot.session.close()

    async def _send_message(
        self,
        bot,
        telegram_id,
        message,
        max_retries=3
    ):
        for attempt in range(max_retries):
            try:
                await bot.send_message(
                    chat_id=telegram_id,
                    text=message,
                    parse_mode="HTML"
                )

                return True

            except TelegramAPIError as e:
                logger.warning(
                    f"Попытка {attempt + 1}/{max_retries} "
                    f"отправки пользователю {telegram_id} "
                    f"не удалась: {e}"
                )

                if attempt == max_retries - 1:
                    logger.exception(
                        f"Не удалось отправить уведомление "
                        f"пользователю {telegram_id} "
                        f"после {max_retries} попыток"
                    )
                    return False

                await asyncio.sleep(2 ** attempt)

            except Exception:
                logger.exception(
                    f"Ошибка отправки пользователю {telegram_id}"
                )
                return False


telegram_service = TelegramService()