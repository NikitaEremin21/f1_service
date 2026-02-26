from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru
from services.calendar_service import (get_next_race,
                                       get_next_race_message)
from django.utils.timezone import get_current_timezone


router = Router()


@router.message(Command("next_race"))
async def next_race(message):
    try:
        user_id = message.from_user.id
        next_race_message = await sync_to_async(get_next_race)(user_id)
        await message.answer(next_race_message)
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении следующей гонки: {e}')
        await message.answer('Ошибка при получении следующей гонки')