from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiohttp import ClientResponseError
from loguru import logger
from tg_bot.keyboards.inline import get_settings_keyboard
from tg_bot.keyboards.inline.settings import (
    get_about_project_keyboard,
    get_back_to_about_project_keyboard,
)
from tg_bot.keyboards.reply.main_menu import (
    MainMenuButtons,
    get_feedback_menu,
    get_main_menu,
)
from tg_bot.states.settings import Feedback, SettingsCity
from aiogram.types import ReplyKeyboardRemove
from tg_bot.services.api_client import backend_client
from django.conf import settings


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
async def show_about_project(callback, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "ℹ️ <b>О проекте</b>\n\nВыберите раздел:",
        parse_mode="HTML",
        reply_markup=get_about_project_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "about_me")
async def show_about_me(callback, state: FSMContext):
    await state.clear()
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
async def show_leave_feedback(callback, state: FSMContext):
    await state.set_state(Feedback.waiting_for_message)
    await callback.message.edit_text(
        "💬 Буду рад анонимному отзыву — отправь его, пожалуйста, одним сообщением.\n\n"
        "Расскажи, что тебе нравится, что можно улучшить, "
        "что работает не так или чего не хватает.\n\n"
        "Буду очень благодарен за обратную связь! 💙",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[])
    )
    await callback.message.answer(
        "Чтобы отменить ввод отзыва, нажми кнопку ниже.",
        reply_markup=get_feedback_menu()
    )
    await callback.answer()


@router.message(
    Feedback.waiting_for_message,
    F.text == MainMenuButtons.CANCEL_FEEDBACK
)
async def cancel_feedback_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отзыв не отправлен.",
        reply_markup=get_main_menu()
    )


@router.message(Feedback.waiting_for_message)
async def receive_feedback(message: Message, state: FSMContext, bot: Bot):
    feedback_text = (message.text or "").strip()
    if not feedback_text:
        await message.answer(
            "Пожалуйста, отправь отзыв текстом. Чтобы выйти, нажми «Отменить отзыв»."
        )
        return

    if len(feedback_text) > 3900:
        await message.answer(
            "Отзыв слишком длинный. Сократи его до 3900 символов и отправь ещё раз."
        )
        return

    if not settings.FEEDBACK_CHANNEL_ID:
        logger.error("FEEDBACK_CHANNEL_ID не настроен; отзыв не отправлен.")
        await state.clear()
        await message.answer(
            "Сейчас не удалось отправить отзыв. Попробуй позже.",
            reply_markup=get_main_menu()
        )
        return

    try:
        await bot.send_message(
            chat_id=settings.FEEDBACK_CHANNEL_ID,
            text=f"\n\n✅ Новый отзыв\n\n{feedback_text}"
        )
    except TelegramAPIError:
        logger.exception("Не удалось отправить отзыв в канал обратной связи.")
        await message.answer(
            "Не удалось отправить отзыв. Попробуй ещё раз или нажми «Отменить отзыв»."
        )
        return

    await state.clear()
    await message.answer(
        "Спасибо за отзыв! 💙",
        reply_markup=get_main_menu()
    )


@router.callback_query(F.data == "support_project")
async def show_support_project(callback, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "💛 Здесь появится информация о том, как поддержать проект.",
        parse_mode="HTML",
        reply_markup=get_back_to_about_project_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "settings_back")
async def back_to_settings(callback, state: FSMContext):
    await state.clear()
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