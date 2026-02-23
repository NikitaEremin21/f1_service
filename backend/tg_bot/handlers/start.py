from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from states.registration import Registration
from services.user_service import (
    create_user,
    set_timezone,
    get_user_by_telegram_id,
)


router = Router()

@router.message(CommandStart())
async def start_function(message, state):
    await state.set_state(Registration.waiting_for_city)
    await sync_to_async(create_user)(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    text = (
        'Добро пожаловать в F1 Assistant!\n'
        f'{message.from_user.first_name}, в каком городе ты живешь?'
    )

    await message.answer(text)


@router.message(Registration.waiting_for_city)
async def user_city_handler(message, state):
    tg_id = message.from_user.id
    user = await sync_to_async(get_user_by_telegram_id)(tg_id)
    timezone = await sync_to_async(set_timezone)(user, message.text)
    if not timezone:
        await message.answer(
            'К сожалению, я не знаю такого города. Пожалуйста, попробуйте еще раз.'
        )
        return
    await message.answer(f'Часовой пояс установлен: {timezone}')

    await state.clear()