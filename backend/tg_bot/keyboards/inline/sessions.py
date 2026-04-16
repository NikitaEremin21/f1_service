from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from core.models import GrandPrix
from django.utils import timezone
from loguru import logger


SESSION_LABELS = {
    "fp1_datetime": "FP1",
    "fp2_datetime": "FP2",
    "fp3_datetime": "FP3",
    "sprint_qualifying_datetime": "SQ",
    "sprint_datetime": "Sprint",
    "qualifying_datetime": "Q",
    "race_datetime": "Race"
}


def get_session_buttons(race):
    """
    Возвращает InlineKeyboard с кнопками пройденных сессий
    """
    now = timezone.now()
    builder = InlineKeyboardBuilder()

    if race.has_sprint:
        sessions = [
            "fp1_datetime",
            "sprint_qualifying_datetime",
            "sprint_datetime",
            "qualifying_datetime",
            "race_datetime",
        ]
    else:
        sessions = [
            "fp1_datetime",
            "fp2_datetime",
            "fp3_datetime",
            "qualifying_datetime",
            "race_datetime",
        ]

    for field in sessions:
        session_time = getattr(race, field)
        if session_time and session_time <= now:
            builder.add(
                InlineKeyboardButton(
                    text=SESSION_LABELS.get(field, field),
                    callback_data=f"session:{race.round}:{field}"
                )
            )

    if not list(builder.buttons):
        return None
    
    builder.adjust(3)
    return builder.as_markup()

