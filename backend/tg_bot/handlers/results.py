from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from loguru import logger
from services.race_service import get_relevant_race
from services.result_service import get_session_results
from services.utils import GP_FLAGS
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from tg_bot.keyboards.inline import get_session_buttons
from tg_bot.services.api_client import backend_client


router = Router()


@router.message(F.text == MainMenuButtons.RESULTS)
@router.message(Command("results"))
async def results_menu(message):
    try:
        race = await backend_client.get_relevant_race()

        if race is None:
            await message.answer(
                "🏁 Информация о гонках пока недоступна.\n\n"
                "Сезон еще не начался или данные загружаются.",
                reply_markup=get_main_menu()
            )
            return
        
        keyboard = get_session_buttons(race)
        race_name = race.get("name") 
        if keyboard:
            await message.answer(
                f"{GP_FLAGS.get(race_name)} {race_name} {GP_FLAGS.get(race_name)}\n\nВыберите сессию:",
                reply_markup=keyboard
            )
        else:
            await message.answer(f"🏁 {race_name} еще не начался.")
    except Exception as e:
        logger.error(f"Ошибка при выводе меню результатов: {e}")
        await message.answer(f"Ошибка при выводе меню результатов.")


@router.callback_query(F.data.startswith("session:"))
async def session_results(callback):
    try:
        i, race_round, session_field = callback.data.split(":")
        text = await get_session_results(race_round, session_field)
        await callback.message.answer(text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка при обработке сессии: {e}")
        await callback.message.answer("Не удалось загрузить результаты.")
