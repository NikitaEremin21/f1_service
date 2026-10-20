from uuid import UUID, uuid4

from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramAPIError
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
)
from aiohttp import ClientResponseError
from loguru import logger
from tg_bot.keyboards.inline import get_settings_keyboard
from tg_bot.keyboards.inline.settings import (
    get_about_project_keyboard,
    get_back_to_about_project_keyboard,
    get_cancel_support_amount_keyboard,
    get_support_methods_keyboard,
    get_support_invoice_keyboard,
    get_support_stars_keyboard,
)
from tg_bot.keyboards.reply.main_menu import (
    MainMenuButtons,
    get_city_change_menu,
    get_feedback_menu,
    get_main_menu,
)
from tg_bot.states.settings import Feedback, SettingsCity, SupportStars
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
        "💛 Если тебе нравится проект, ты можешь поддержать его.\n"
        "Доступные способы:",
        parse_mode="HTML",
        reply_markup=get_support_methods_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "support_stars_menu")
async def show_support_stars_menu(callback, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Выбери сумму из предложенных или введи свою:",
        reply_markup=get_support_stars_keyboard()
    )
    await callback.answer()


async def send_support_invoice(bot: Bot, chat_id: int, amount: int):
    payload = f"project_support:{amount}:{uuid4().hex}"
    await bot.send_invoice(
        chat_id=chat_id,
        title="Поддержка проекта",
        description="Разовая добровольная поддержка проекта F1 Service (Не является подпиской).",
        payload=payload,
        provider_token="",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Поддержка проекта",
                amount=amount
            )
        ],
        reply_markup=get_support_invoice_keyboard(amount),
    )


async def begin_support_payment(bot: Bot, chat_id: int, amount: int):
    await send_support_invoice(bot, chat_id, amount)


@router.callback_query(F.data == "support_invoice_cancel")
async def cancel_support_invoice(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.delete()
    except TelegramAPIError:
        logger.exception("Не удалось удалить отменённый счёт поддержки.")

    await callback.message.answer(
        "ℹ️ <b>О проекте</b>\n\nВыберите раздел:",
        parse_mode="HTML",
        reply_markup=get_about_project_keyboard()
    )
    await callback.answer("Поддержка отменена.")


@router.callback_query(F.data.startswith("support_stars:"))
async def support_with_stars(callback: CallbackQuery, state: FSMContext, bot: Bot):
    try:
        amount = int(callback.data.rsplit(":", maxsplit=1)[1])
    except (ValueError, IndexError):
        await callback.answer("Некорректная сумма.", show_alert=True)
        return

    if amount not in (10, 30, 50, 100, 200, 500):
        await callback.answer("Некорректная сумма.", show_alert=True)
        return

    try:
        await begin_support_payment(
            bot,
            callback.message.chat.id,
            amount,
        )
    except TelegramAPIError:
        logger.exception("Не удалось создать счёт поддержки в Stars.")
        await callback.answer(
            "Не удалось создать счёт. Попробуй ещё раз позже.",
            show_alert=True
        )
        return

    try:
        await callback.message.delete()
    except TelegramAPIError:
        logger.exception("Не удалось удалить меню выбора суммы после отправки счёта.")
    await callback.answer()


@router.callback_query(F.data == "support_custom_amount")
async def request_support_amount(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SupportStars.waiting_for_amount)
    await state.update_data(support_menu_message_id=callback.message.message_id)
    await callback.message.edit_text(
        "Введи целое количество Stars. Сумма должна быть больше нуля.\n\n"
        "Если передумал, нажми «Отменить».",
        reply_markup=get_cancel_support_amount_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "support_amount_cancel")
async def cancel_support_amount(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "💛 Если тебе нравится проект, ты можешь поддержать его.\n"
        "Доступные способы:",
        reply_markup=get_support_methods_keyboard()
    )
    await callback.answer("Ввод суммы отменён.")


@router.message(SupportStars.waiting_for_amount)
async def process_support_amount(message: Message, state: FSMContext, bot: Bot):
    amount_text = (message.text or "").strip()
    if not amount_text.isascii() or not amount_text.isdecimal():
        await message.answer("Введи сумму целым числом больше нуля.")
        return

    try:
        amount = int(amount_text)
    except ValueError:
        await message.answer("Не удалось распознать сумму. Введи целое число Stars.")
        return

    if amount <= 0:
        await message.answer("Сумма должна быть больше нуля. Введи другое число.")
        return

    state_data = await state.get_data()
    menu_message_id = state_data.get("support_menu_message_id")
    try:
        await begin_support_payment(
            bot,
            message.chat.id,
            amount,
        )
    except TelegramAPIError:
        logger.exception("Не удалось создать счёт поддержки на пользовательскую сумму.")
        await message.answer(
            "Telegram не принял эту сумму. Проверь её или попробуй ввести меньшую."
        )
        return

    await state.clear()
    if menu_message_id:
        try:
            await bot.delete_message(
                chat_id=message.chat.id,
                message_id=menu_message_id
            )
        except TelegramAPIError:
            logger.exception("Не удалось удалить запрос суммы после отправки счёта.")


@router.pre_checkout_query()
async def confirm_support_payment(query: PreCheckoutQuery):
    try:
        prefix, amount_text, payload_id = query.invoice_payload.split(":", maxsplit=2)
        expected_amount = int(amount_text)
        valid = (
            prefix == "project_support"
            and expected_amount > 0
            and query.currency == "XTR"
            and query.total_amount == expected_amount
            and UUID(payload_id).version == 4
        )
    except (ValueError, TypeError, AttributeError):
        valid = False

    await query.answer(
        ok=valid,
        error_message=None if valid else "Не удалось проверить счёт. Создай новый счёт в меню поддержки."
    )


@router.message(F.successful_payment)
async def confirm_support_payment_success(message: Message, state: FSMContext):
    payment = message.successful_payment
    try:
        prefix, expected_amount_text, payload_id = payment.invoice_payload.split(":", maxsplit=2)
        valid_payment = (
            prefix == "project_support"
            and payment.currency == "XTR"
            and payment.total_amount == int(expected_amount_text)
            and payment.total_amount > 0
            and UUID(payload_id).version == 4
        )
    except (ValueError, TypeError, AttributeError):
        valid_payment = False

    if not valid_payment:
        logger.error("Получено платёжное уведомление с некорректными данными счёта.")
        await message.answer(
            "Платёж получен, но возникла ошибка при подтверждении. Напиши в поддержку проекта."
        )
        return

    await state.clear()
    await message.answer(
        f"Спасибо за поддержку проекта — получено {payment.total_amount} ⭐! 💙",
        reply_markup=get_main_menu()
    )


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
        reply_markup=get_city_change_menu(),
    )
    await callback.answer()


@router.message(
    SettingsCity.waiting_for_new_city,
    F.text == MainMenuButtons.CANCEL_CITY_CHANGE
)
async def cancel_city_change(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Смена города отменена.",
        reply_markup=get_main_menu()
    )


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