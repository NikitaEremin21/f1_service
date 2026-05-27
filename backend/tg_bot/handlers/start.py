from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from tg_bot.states.registration import Registration
from tg_bot.keyboards.reply import get_main_menu
from tg_bot.services.api_client import backend_client
from loguru import logger


router = Router()


@router.message(CommandStart())
async def start_function(message, state):
    await state.set_state(Registration.waiting_for_city)

    await backend_client.create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    await message.answer(
        'Добро пожаловать в F1 Assistant!\n'
        f'{message.from_user.first_name}, в каком городе ты живешь?'
    )


@router.message(Registration.waiting_for_city)
async def user_city_handler(message, state):

    tg_id = message.from_user.id
    text = message.text
    logger.info(f"User {tg_id} entered city: {text}")
    result = await backend_client.set_user_timezone(tg_id, text)
    
    if not result or not result.get("timezone"):
        await message.answer(
            'К сожалению, я не знаю такого города. Пожалуйста, попробуйте еще раз.'
        )
        return
    
    await message.answer(
        f'Часовой пояс установлен: {result.get("timezone")}',
        reply_markup=get_main_menu(),
    )

    await state.clear()