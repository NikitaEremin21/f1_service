from aiogram import Router, F
from aiogram.filters import Command
from aiohttp import ClientResponseError
from loguru import logger
from tg_bot.keyboards.inline import get_settings_keyboard
from tg_bot.keyboards.inline.settings import get_about_project_keyboard, get_back_to_about_project_keyboard
from tg_bot.keyboards.reply.main_menu import MainMenuButtons, get_main_menu
from tg_bot.states.settings import SettingsCity
from aiogram.types import ReplyKeyboardRemove
from tg_bot.services.api_client import backend_client


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


@router.callback_query(F.data == "about_project")
async def show_about_project(callback):
    await callback.message.edit_text(
        "ℹ️ <b>О проекте</b>\n\nВыберите раздел:",
        parse_mode="HTML",
        reply_markup=get_about_project_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "about_me")
async def show_about_me(callback):
    await callback.message.edit_text(
        "Привет! 👋\n\n"
        "Меня зовут Никита, и я начинающий разработчик, который давно любит Формулу 1.\n\n"
        "💡 Идея этого проекта появилась из желания сделать удобный сервис для фанатов - чтобы информация была ближе, "
        "понятнее и всегда под рукой. \n\n"
        "🚀 Проект только начинает свой путь, и он ещё активно развивается. Я очень благодарен тем, кто поддерживает идею, "
        "тестирует её, делится мнением и помогает становиться лучше. 🙏\n\n"
        "💬 Если у тебя есть замечания, идеи или просто хочется "
        "сказать, что нравится — буду рад любой обратной связи. \n\n"
        "Спасибо, что остаешься рядом и помогаешь проекту расти. 💙",
        parse_mode="HTML",
        reply_markup=get_back_to_about_project_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "leave_feedback")
async def show_leave_feedback(callback):
    await callback.message.edit_text(
        "💬 Здесь будет возможность оставить отзыв.",
        parse_mode="HTML",
        reply_markup=get_back_to_about_project_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "support_project")
async def show_support_project(callback):
    await callback.message.edit_text(
        "💛 Здесь появится информация о том, как поддержать проект.",
        parse_mode="HTML",
        reply_markup=get_back_to_about_project_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "settings_back")
async def back_to_settings(callback):
    await callback.message.edit_text(
        "⚙️ **Настройки**\n\nВыберите параметр для настройки:",
        parse_mode="Markdown",
        reply_markup=get_settings_keyboard()
    )
    await callback.answer()


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
    try:
        user_id = message.from_user.id
        city = message.text.strip()

        user_data = await backend_client.set_user_timezone(user_id, city)
        if not user_data:
            await message.answer(
                "❌ Не удалось определить часовой пояс для этого города.\n"
                "Попробуйте еще раз."
            )
            return    
        
        await message.answer(
            f"✅ Часовой пояс успешно обновлен: {user_data.get('timezone')}\n\n"
            f"📍 Город: {city}",
            reply_markup=get_main_menu()
        )
        await state.clear()
    except ClientResponseError as e:
        if e.status == 404:
            await message.answer("Пользователь не найден. Пожалуйста, перезапустите бота командой /start.")
        else:
            logger.error(f"HTTP ошибка при смене города: {e.status}")
            await message.answer("Сервис временно недоступен. Попробуйте позже.")
    except Exception as e:
        logger.exception(f"Ошибка при смене города: {e}")
        await message.answer("Произошла ошибка при смене города. Попробуйте позже.")    