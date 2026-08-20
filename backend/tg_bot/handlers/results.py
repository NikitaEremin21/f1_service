from aiogram import Router, F
from aiogram.filters import Command
from loguru import logger
from services.utils import GP_FLAGS, PRACTICE_SESSIONS
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from tg_bot.keyboards.inline import get_session_buttons
from tg_bot.services.api_client import backend_client
from tg_bot.formatters.results_formatter import (
    get_format_practice_message,
    get_format_qualifying_message,
    get_format_race_message
)
from aiohttp import ClientResponseError


router = Router()


@router.message(F.text == MainMenuButtons.RESULTS)
@router.message(Command("results"))
async def results_menu(message):
    try:
        race = await backend_client.get_relevant_race()        
        keyboard = get_session_buttons(race)
        race_name = race.get("name") 
        if keyboard:
            await message.answer(
                f"{GP_FLAGS.get(race_name)} {race_name} {GP_FLAGS.get(race_name)}\n\nВыберите сессию:",
                reply_markup=keyboard
            )
        else:
            await message.answer(f"🏁 {race_name} еще не начался.")
    except ClientResponseError as e:
        if e.status == 404:
             await message.answer(
                            "🏁 Информация о гонках пока недоступна.\n\n"
                            "Сезон еще не начался или данные загружаются.",
                            reply_markup=get_main_menu()
                        )
        else:
            logger.error(f"HTTP ошибка при запросе результатов: {e.status}")
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка при выводе меню результатов: {e}")
        await message.answer(f"Ошибка при выводе меню результатов.")


@router.callback_query(F.data.startswith("session:"))
async def session_results(callback):
    try:
        _, race_round, session_field = callback.data.split(":")
        session_name = session_field.replace("_datetime", "")

        result_data = await backend_client.get_session_results(race_round, session_name)
        if not result_data:
            await callback.message.answer("Результаты для этой сессии пока недоступны.")
            return
        
        session_type = result_data.get("session")

        if session_type in PRACTICE_SESSIONS:
            text = await get_format_practice_message(result_data)
        elif session_type == "qualifying" or session_type == "sprint_qualifying":
            text = await get_format_qualifying_message(result_data)
        else:
            text = await get_format_race_message(result_data)

        await callback.message.answer(text, parse_mode="HTML")

    except Exception as e:
        logger.exception(f"Ошибка при обработке сессии: {e}")
        await callback.message.answer("Не удалось загрузить результаты.")
