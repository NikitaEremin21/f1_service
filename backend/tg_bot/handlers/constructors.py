from aiogram import Router, F
from aiogram.filters import Command
from aiohttp import ClientResponseError
from loguru import logger
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from tg_bot.services.api_client import backend_client
from tg_bot.formatters.constructors_formatter import format_constructors_message


router = Router()


@router.message(F.text == MainMenuButtons.TEAMS_LIST)
@router.message(Command("constructors"))
async def constructors_list(message):
    try:
        constructors = await backend_client.get_all_constructors()
        if not constructors:
            await message.answer("Список команд временно недоступен.", reply_markup=get_main_menu())
            return  
        text = format_constructors_message(constructors)
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    except ClientResponseError as e:
        if e.status == 404:
            await message.answer("Список команд не найден.", reply_markup=get_main_menu())
        else:
            logger.error(f"HTTP ошибка при получении списка команд: {e.status}")
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
    except Exception as e:
        logger.exception(f'Ошибка при получении списка команд: {e}')
        await message.answer('Ошибка при получении списка команд')