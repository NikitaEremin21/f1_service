from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
import loguru
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from services.calendar_service import get_next_race
from services.user_service import create_user
from tg_bot.states.registration import Registration


router = Router()


@router.message(F.text == MainMenuButtons.NEXT_RACE)
@router.message(Command("next_race"))
async def next_race(message, state):
    try:
        user_id = message.from_user.id
        next_race_message = await sync_to_async(get_next_race)(user_id)

        if next_race_message is None:
            await state.set_state(Registration.waiting_for_city)
            await sync_to_async(create_user)(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
            )
            await message.answer(
                f"❌ Ваш профиль не найден в базе данных.\n"
                f"Необходимо пройти регистрацию повторно.\n"
                f"{message.from_user.first_name}, в каком городе ты живешь?"
            )
            return
        
        await message.answer(
            next_race_message,
            reply_markup=get_main_menu()
        )
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении следующей гонки: {e}')
        await message.answer('Ошибка при получении следующей гонки')