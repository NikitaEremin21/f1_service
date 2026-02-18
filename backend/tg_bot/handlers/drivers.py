from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru

from services.driver_service import (get_drivers_list,
                                     format_drivers_list)


router = Router()


@router.message(Command("drivers"))
async def drivers_list(message):
    try:
        drivers = await sync_to_async(get_drivers_list)()
        text = format_drivers_list(drivers)
        await message.answer(text)
        
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении списка пилотов: {e}')
        await message.answer('Ошибка при получении списка пилотов')




