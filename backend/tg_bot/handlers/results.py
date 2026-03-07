from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from loguru import logger
from services.race_service import get_relevant_race
from keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from keyboards.inline import get_session_buttons


router = Router()


@router.message(F.text == MainMenuButtons.RESULTS)
@router.message(Command("results"))
async def results_menu(message):
    try:
        race = await sync_to_async(get_relevant_race)()
        keyboard = get_session_buttons(race)
        if keyboard:
            await message.answer(
                f"🏁 {race.name}\n\nВыберите сессию:",
                reply_markup=keyboard
            )
        else:
            await message.answer(f"🏁 {race.name} еще не начался.")
    except Exception as e:
        logger.error(f"Ошибка при выводе меню результатов: {e}")
        await message.answer(f"Ошибка при выводе меню результатов.")