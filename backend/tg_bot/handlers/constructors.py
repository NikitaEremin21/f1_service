from aiogram import Router, F
from aiogram.filters import Command
import loguru
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
        text = format_constructors_message(constructors)
        await message.answer(
            text, parse_mode="HTML",
            reply_markup=get_main_menu()
        )

    except Exception as e:
        loguru.logger.error(f'Ошибка при получении списка команд: {e}')
        await message.answer('Ошибка при получении списка команд')