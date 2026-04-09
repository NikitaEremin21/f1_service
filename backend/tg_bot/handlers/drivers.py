from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from services.driver_service import (
    get_drivers_list,
    format_drivers_list
)


router = Router()


@router.message(F.text == MainMenuButtons.DRIVERS_LIST)
@router.message(Command("drivers"))
async def drivers_list(message):
    try:
        drivers = await sync_to_async(get_drivers_list)()
        text = format_drivers_list(drivers)
        await message.answer(
            text, parse_mode="HTML",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении списка пилотов: {e}')
        await message.answer('Ошибка при получении списка пилотов')




