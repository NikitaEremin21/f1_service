from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta
import loguru
from core.models import GrandPrix
from .utils import get_calendar_message


router = Router()


@router.message(Command("calendar"))
async def calendar_function(message):
    try:
        data = await sync_to_async(
            lambda: list(
                GrandPrix.objects.select_related('circuit').order_by('round').all()
            )
        )()
        calendar_text = get_calendar_message(data)
        await message.answer(calendar_text)
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении календаря: {e}')
        await message.answer('Ошибка при получении календаря')