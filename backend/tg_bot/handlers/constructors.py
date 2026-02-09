from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru

from core.models import Constructor


router = Router()


def format_constructors_list(constructors):
    text = "Список команд формулы 1 сезон 2026: \n\n"
    for i, constructor in enumerate(constructors, 1):
        text += f"{i}. {constructor.name} - {constructor.nationality}\n"
    return text


@router.message(Command("constructors"))
async def get_constructors_list(message):
    try:
        constructors = await sync_to_async(
            lambda: list(
                Constructor.objects.all())
        )()

        text = format_constructors_list(constructors)
        await message.answer(text)

    except Exception as e:
        loguru.logger.error(f'Ошибка при получении списка команд: {e}')
        await message.answer('Ошибка при получении списка команд')