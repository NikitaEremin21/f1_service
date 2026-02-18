from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru

from services.constructor_service import (get_constructors_list,
                                          format_constructors_list)


router = Router()


@router.message(Command("constructors"))
async def constructors_list(message):
    try:
        constructors = await sync_to_async(get_constructors_list)()
        text = format_constructors_list(constructors)
        await message.answer(text)

    except Exception as e:
        loguru.logger.error(f'Ошибка при получении списка команд: {e}')
        await message.answer('Ошибка при получении списка команд')