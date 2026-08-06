from aiogram import Router, F
from aiogram.filters import Command
from aiohttp import ClientResponseError
from asgiref.sync import sync_to_async
from loguru import logger
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from tg_bot.services.api_client import backend_client
from tg_bot.formatters.drivers_formatter import format_drivers_message


router = Router()


@router.message(F.text == MainMenuButtons.DRIVERS_LIST)
@router.message(Command("drivers"))
async def drivers_list(message):
    try:
        drivers = await backend_client.get_all_drivers()
        if not drivers:
            await message.answer("Список пилотов временно недоступен.", reply_markup=get_main_menu())
            return
        text = await sync_to_async(format_drivers_message)(drivers)
        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    except ClientResponseError as e:
        if e.status == 404:
            await message.answer("Список пилотов не найден.", reply_markup=get_main_menu())
        else:
            logger.error(f"HTTP ошибка при получении списка пилотов: {e.status}")
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
    except Exception as e:
        logger.error(f'Ошибка при получении списка пилотов: {e}')
        await message.answer('Ошибка при получении списка пилотов')




