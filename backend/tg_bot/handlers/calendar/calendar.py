from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from loguru import logger
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from tg_bot.formatters.calendar_formatter import format_calendar_message
from tg_bot.services.api_client import backend_client


router = Router()


@router.message(F.text == MainMenuButtons.CALENDAR)
@router.message(Command("calendar"))
async def calendar_function(message):
    try:
        data = await backend_client.get_calendar()
        calendar_text = format_calendar_message(data)
        await message.answer(
            calendar_text,
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logger.error(f'Ошибка при получении календаря: {e}')
        await message.answer('Ошибка при получении календаря')