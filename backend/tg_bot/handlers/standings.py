from aiogram import Router, F
from aiogram.filters import Command
from aiohttp import ClientResponseError
from tg_bot.services.api_client import backend_client
from loguru import logger
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from tg_bot.formatters.standings_formatter import (
    get_format_championship_drivers_message,
    get_format_championship_teams_message,
)


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
        
        text = get_format_championship_drivers_message(championship_drivers)
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    except ClientResponseError as e:
        if e.status == 404:
            await message.answer("Чемпионат пилотов не найден.", reply_markup=get_main_menu())
        else:
            logger.error(f"HTTP ошибка при выводе чемпионата пилотов: {e.status}")
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка при выводе чемпионата пилотов: {e}")
        await message.answer(f"Ошибка при выводе чемпионата пилотов.")


@router.message(F.text == MainMenuButtons.TEAMS_STANDINGS)
@router.message(Command("teams_standings"))
async def teams_standings(message):
    try:
        championship_teams = await backend_client.get_standings_teams()
        if not championship_teams:
            await message.answer(
                "Кубок конструкторов временно недоступен.\n\nВозможно, сезон еще не начался.",
                reply_markup=get_main_menu(),
            )
            return

        text = get_format_championship_teams_message(championship_teams)
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    except ClientResponseError as e:
        if e.status == 404:
            await message.answer("Кубок конструкторов не найден.", reply_markup=get_main_menu())
        else:
            logger.error(f"HTTP ошибка при выводе кубка конструкторов: {e.status}")
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка при выводе кубка конструкторов: {e}")
        await message.answer(f"Ошибка при выводе кубка конструкторов.")