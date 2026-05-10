from aiogram import Router, F
from aiogram.filters import Command
from tg_bot.services.api_client import backend_client
from loguru import logger
from services.standing_service import (
    get_drivers_standings,
    get_teams_standings
)
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from tg_bot.formatters.standings_formatter import (
    get_format_championship_drivers_message,
)
from asgiref.sync import sync_to_async


router = Router()


@router.message(F.text == MainMenuButtons.DRIVERS_STANDINGS)
@router.message(Command("drivers_standings"))
async def drivers_standings(message):
    try:
        championship_drivers = await backend_client.get_standings_drivers()

        if not championship_drivers or not championship_drivers.get("standings"):
            await message.answer(
                "Чемпионат пилотов временно недоступен.\n\nВозможно, сезон еще не начался.",
                reply_markup=get_main_menu(),
            )
            return
        
        text = await sync_to_async(get_format_championship_drivers_message)(championship_drivers)
        await message.answer(
            text, parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка при выводе чемпионата пилотов: {e}")
        await message.answer(f"Ошибка при выводе чемпионата пилотов.")


@router.message(F.text == MainMenuButtons.TEAMS_STANDINGS)
@router.message(Command("teams_standings"))
async def teams_standings(message):
    try:
        text = await get_teams_standings()
        await message.answer(
            text, parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка при выводе кубка конструкторов: {e}")
        await message.answer(f"Ошибка при выводе кубка конструкторов.")