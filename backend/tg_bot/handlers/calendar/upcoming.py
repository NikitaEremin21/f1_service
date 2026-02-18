from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from django.utils import timezone
import loguru
from core.models import GrandPrix
from services.calendar_service import (get_upcoming_races,
                                       get_calendar_message)


router = Router()


@router.message(Command("upcoming"))
async def upcoming_function(message):
    try:
        data = await sync_to_async(get_upcoming_races)()
        calendar_text = get_calendar_message(data)
        await message.answer(calendar_text)
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении календаря: {e}')
        await message.answer('Ошибка при получении календаря')