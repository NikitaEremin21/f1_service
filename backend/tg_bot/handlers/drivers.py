from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru

from core.models import Driver


router = Router()


def formal_drivers_list(drivers):
    text = f"Список пилотов формулы 1 сезон 2026 \n\n"
    for driver in drivers:
        text += f"{driver.number} - {driver.first_name} {driver.last_name} - {driver.team}\n"
    return text


@router.message(Command("drivers"))
async def drivers_list(message):
    try:
        drivers = await sync_to_async(
            lambda: list(
                Driver.objects.select_related('team').all()
            ))()
        
        text = formal_drivers_list(drivers)
        await message.answer(text)
        
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении списка пилотов: {e}')
        await message.answer('Ошибка при получении списка пилотов')




