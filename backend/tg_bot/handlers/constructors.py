from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru
from keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from services.constructor_service import (
    get_constructors_list,
    format_constructors_list
)


router = Router()


@router.message(F.text == MainMenuButtons.TEAMS_LIST)
@router.message(Command("constructors"))
async def constructors_list(message):
    try:
        constructors = await sync_to_async(get_constructors_list)()
        text = format_constructors_list(constructors)
        await message.answer(
            text, parse_mode="HTML",
            reply_markup=get_main_menu()
        )

    except Exception as e:
        loguru.logger.error(f'Ошибка при получении списка команд: {e}')
        await message.answer('Ошибка при получении списка команд')