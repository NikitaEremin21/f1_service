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


def get_support_stars_keyboard():
    builder = InlineKeyboardBuilder()
    for amount in (10, 30, 50, 100, 200, 500):
        builder.button(
            text=f"{amount} ⭐",
            callback_data=f"support_stars:{amount}"
        )
    builder.button(
        text="Другая сумма",
        callback_data="support_custom_amount"
    )
    builder.button(
        text="Назад",
        callback_data="about_project"
    )
    builder.adjust(3, 3, 1, 1)
    return builder.as_markup()


def get_support_methods_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="💸 DonationAlerts",
        url="https://www.donationalerts.com/r/nikita_21e"
    )
    builder.button(
        text="⭐ Telegram Stars",
        callback_data="support_stars_menu"
    )
    builder.button(
        text="Назад",
        callback_data="about_project"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_cancel_support_amount_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отменить",
        callback_data="support_amount_cancel"
    )
    builder.adjust(1)
    return builder.as_markup()


def get_support_invoice_keyboard(amount: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Заплатить ⭐ {amount}",
        pay=True
    )
    builder.button(
        text="Отменить",
        callback_data="support_invoice_cancel"
    )
    builder.adjust(1)
    return builder.as_markup()