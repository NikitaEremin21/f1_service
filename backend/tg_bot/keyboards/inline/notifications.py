from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


ALL_SESSIONS = [
    ("fp1", "FP1"),
    ("fp2", "FP2"),
    ("fp3", "FP3"),
    ("sprint_qualifying", "Sprint Qualifying"),
    ("sprint", "Sprint"),
    ("qualifying", "Qualifying"),
    ("race", "Race"),
]
ALL_REMINDERS = [120, 60, 30, 20, 15, 10]


def get_notifications_keyboard(enabled_sessions, enabled_reminders):
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Сессии для напоминаний:", callback_data="ignore"))

    for session_key, session_label in ALL_SESSIONS:
        is_enabled = session_key in enabled_sessions
        icon = "✅" if is_enabled else "❌"
        callback = f"notif:session:{session_key}:{1 if is_enabled else 0}"
        builder.add(InlineKeyboardButton(
            text=f"{icon} {session_label}",
            callback_data=callback
        ))

    builder.add(InlineKeyboardButton(text="Время напоминаний:", callback_data="ignore"))

    for reminder in ALL_REMINDERS:
        is_enabled = reminder in enabled_reminders
        icon = "✅" if is_enabled else "❌"
        callback = f"notif:reminder:{reminder}:{1 if is_enabled else 0}"
        builder.add(InlineKeyboardButton(
            text=f"{icon} {reminder} мин.",
            callback_data=callback
        ))

    builder.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="notif_back",
    ))

    builder.adjust(1, 3, 2, 2, 1, 3, 3, 1)
    return builder.as_markup()