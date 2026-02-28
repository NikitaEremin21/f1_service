from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru
from keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from services.calendar_service import get_next_race


router = Router()


@router.message(F.text == MainMenuButtons.NEXT_RACE)
@router.message(Command("next_race"))
async def next_race(message):
    try:
        user_id = message.from_user.id
        next_race_message = await sync_to_async(get_next_race)(user_id)
        await message.answer(
            next_race_message,
            reply_markup=get_main_menu()
        )
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении следующей гонки: {e}')
        await message.answer('Ошибка при получении следующей гонки')