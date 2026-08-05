from aiogram import Router, F
from aiogram.filters import Command
from aiohttp import ClientResponseError
from loguru import logger
from tg_bot.keyboards.reply import (
    get_main_menu,
    MainMenuButtons
)
from tg_bot.services.api_client import backend_client
from tg_bot.states.registration import Registration
from tg_bot.formatters.calendar_formatter import get_next_race_message


router = Router()


@router.message(F.text == MainMenuButtons.NEXT_RACE)
@router.message(Command("next_race"))
async def next_race(message, state):
    try:
        user_id = message.from_user.id
        user = await backend_client.get_user(user_id)
        if not user:
            await state.set_state(Registration.waiting_for_city)
            await backend_client.create_user(
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
        
        user_tz = user.get("timezone")
        next_race_data = await backend_client.get_next_race(user_tz)
        next_race_message = get_next_race_message(next_race_data)
        await message.answer(
            next_race_message,
            reply_markup=get_main_menu()
        )
    except ClientResponseError as e:
        if e.status == 404:
            await message.answer(
                "🏁 Сезон ещё не начался или уже завершён.\n\n"
                "Следите за обновлениями календаря.",
                reply_markup=get_main_menu()
            )
        else:
            logger.error(f"HTTP ошибка при получении следующей гонки: {e.status}")
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
    except Exception as e:
        logger.error(f'Ошибка при получении следующей гонки: {e}')
        await message.answer('Ошибка при получении следующей гонки')