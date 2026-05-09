from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru
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
        text = await sync_to_async(format_drivers_message)(drivers)
        await message.answer(
            text, parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении списка пилотов: {e}')
        await message.answer('Ошибка при получении списка пилотов')




