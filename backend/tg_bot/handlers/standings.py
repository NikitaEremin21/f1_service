from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from loguru import logger
from services.standing_service import (
    get_drivers_standings,
    get_teams_standings
)
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)


router = Router()


@router.message(F.text == MainMenuButtons.DRIVERS_STANDINGS)
@router.message(Command("drivers_standings"))
async def drivers_standings(message):
    try:
        text = await sync_to_async(get_drivers_standings)()
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
        text = await sync_to_async(get_teams_standings)()
        await message.answer(
            text, parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка при выводе кубка конструкторов: {e}")
        await message.answer(f"Ошибка при выводе кубка конструкторов.")