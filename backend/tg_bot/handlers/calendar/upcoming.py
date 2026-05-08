from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from tg_bot.services.api_client import backend_client
from tg_bot.formatters.calendar_formatter import format_calendar_message

router = Router()


@router.message(F.text == MainMenuButtons.UPCOMING_RACES)
@router.message(Command("upcoming"))
async def upcoming_function(message):
    try:
        text = f"Предстоящие этапы формулы 1 2026\n\n"
        data = await backend_client.get_upcoming_calendar()
        upcoming_text = format_calendar_message(data, text)
        await message.answer(
            upcoming_text,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении календаря: {e}')
        await message.answer('Ошибка при получении календаря')