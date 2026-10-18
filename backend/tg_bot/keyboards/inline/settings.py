from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


SETTINGS_LABELS = {
    "change_city": "change_city",
    "notifications_menu": "notifications_menu",
    "about_project": "about_project",
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
        ),
        InlineKeyboardButton(
            text="ℹ️ О проекте",
            callback_data=SETTINGS_LABELS["about_project"]
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def get_about_project_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Обо мне",
            callback_data="about_me"
        ),
        InlineKeyboardButton(
            text="Оставить отзыв",
            callback_data="leave_feedback"
        ),
        InlineKeyboardButton(
            text="Поддержать проект",
            callback_data="support_project"
        ),
        InlineKeyboardButton(
            text="Назад",
            callback_data="settings_back"
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def get_back_to_about_project_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Назад",
            callback_data="about_project"
        )
    )
    return builder.as_markup()