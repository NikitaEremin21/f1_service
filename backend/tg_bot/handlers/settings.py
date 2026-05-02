from aiogram import Router, F
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from services.user_service import get_user_by_telegram_id, set_timezone
from tg_bot.keyboards.inline import get_settings_keyboard
from tg_bot.keyboards.reply.main_menu import MainMenuButtons, get_main_menu
from tg_bot.states.settings import SettingsCity
from aiogram.types import ReplyKeyboardRemove


router = Router()


@router.message(F.text == MainMenuButtons.SETTINGS)
@router.message(Command("settings"))
async def show_settings(message):
    await message.answer(
        "⚙️ **Настройки**\n\n"
        "Выберите параметр для настройки:",
        parse_mode="Markdown",
        reply_markup=get_settings_keyboard()
    )


@router.callback_query(F.data == "change_city")
async def change_city_callback(callback, state):
    """
    Запрашивает новый город у пользователя
    """
    await state.set_state(SettingsCity.waiting_for_new_city)
    await callback.message.answer(
        "🌍 **Смена города**\n\n"
        "Пожалуйста, введите название города:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    await callback.answer()


@router.message(SettingsCity.waiting_for_new_city)
async def process_new_city(message, state):
    """
    Обрабатывает новый город, введенный пользователем
    """
    user_id = message.from_user.id
    city = message.text.strip()

    user = await sync_to_async(get_user_by_telegram_id)(user_id)
    timezone = await sync_to_async(set_timezone)(user, city)

    if not timezone:
        await message.answer(
            "❌ Не удалось определить часовой пояс для этого города.\n"
            "Попробуйте еще раз."
        )
        return    
    
    await message.answer(
        f"✅ Часовой пояс успешно обновлен: {timezone}\n\n"
        f"📍 Город: {city}",
        reply_markup=get_main_menu()
    )
    await state.clear()