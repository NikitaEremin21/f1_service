from aiogram.types import Message, CallbackQuery
from tg_bot.keyboards.inline.notifications import get_notifications_keyboard
from aiogram.exceptions import TelegramBadRequest


async def render_notifications_keyboard(target, state, enabled_sessions, enabled_reminders):
    """
    Отправить или обновить клавиатуру с настройками уведомлений
    """
    await state.update_data(
        enabled_sessions=enabled_sessions,
        enabled_reminders=enabled_reminders
    )
    text = (
        "🔔 <b>Настройка напоминаний</b>\n\n"
        "Выберите, о каких событиях и за сколько времени присылать уведомления."
    )
    keyboard = get_notifications_keyboard(enabled_sessions, enabled_reminders)

    try:
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
        else:
            await target.edit_text(
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard
            )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            raise