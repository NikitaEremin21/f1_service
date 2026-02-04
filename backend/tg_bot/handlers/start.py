from aiogram import Router
from aiogram.filters import CommandStart


router = Router()

@router.message(CommandStart())
async def start_function(message):
    text = (
        'Добро пожаловать в F1 Assistant!'
    )

    await message.answer(text)