from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru
from keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from services.calendar_service import (
    get_upcoming_races,
    get_calendar_message
)


router = Router()


@router.message(F.text == MainMenuButtons.UPCOMING_RACES)
@router.message(Command("upcoming"))
async def upcoming_function(message):
    try:
        data = await sync_to_async(get_upcoming_races)()
        calendar_text = get_calendar_message(data)
        await message.answer(
            calendar_text,
            reply_markup=get_main_menu()
        )
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении календаря: {e}')
        await message.answer('Ошибка при получении календаря')