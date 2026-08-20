from aiogram import Router, F
from aiogram.filters import Command
from aiohttp import ClientResponseError
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
        text = f"Календарь формулы 1 2026\n\n"
        data = await backend_client.get_calendar()
        if not data:
            await message.answer("Календарь временно недоступен.", reply_markup=get_main_menu())
            return
        calendar_text = format_calendar_message(data, text)
        await message.answer(
            calendar_text,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    except ClientResponseError as e:
        if e.status == 404:
            await message.answer("Календарь временно недоступен.", reply_markup=get_main_menu())
        else:
            logger.error(f"HTTP ошибка при получении календаря: {e.status}")
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
    except Exception as e:
        logger.exception(f'Ошибка при получении календаря: {e}')
        await message.answer('Ошибка при получении календаря')