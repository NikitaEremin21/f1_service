from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


SETTINGS_LABELS = {
    "change_city": "change_city",
    "notifications_menu": "notifications_menu",
}

def get_settings_keyboard():
    """
    Возвращает InlineKeyboard с кнопками настроек
    """
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="🌍 Изменить город",
            callback_data=SETTINGS_LABELS["change_city"]
        ),
        InlineKeyboardButton(
            text="🔔 Настройки уведомлений",
            callback_data=SETTINGS_LABELS["notifications_menu"]
        )
    )
    builder.adjust(1)
    return builder.as_markup()