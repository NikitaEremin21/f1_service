from datetime import datetime, timedelta
from django.utils import timezone
from core.models import GrandPrix
from zoneinfo import ZoneInfo
from collections import defaultdict
from services.utils import (
    format_date,
    GP_FLAGS,
)
from services.user_service import get_user_by_telegram_id
from loguru import logger


SESSION_LABELS = {
    "fp1_datetime": "FP1",
    "fp2_datetime": "FP2",
    "fp3_datetime": "FP3",
    "sprint_qualifying_datetime": "SQ",
    "sprint_datetime": "Sprint",
    "qualifying_datetime": "Q",
    "race_datetime": "R",
}


def format_calendar_message(races, text):
    """
    Формирует сообщение календаря
    """
    for race in races:
        if isinstance(race['date'], str):
            date_obj = datetime.strptime(race['date'], '%Y-%m-%d').date()
        else:
            date_obj = race['date'] 
        date = format_date(date_obj)
        flag = GP_FLAGS.get(race['name'], "")
        circuit_name = race.get('circuit_name', 'Неизвестно')
        if race['has_sprint']:
            text += (
                f"{race['round']}. {flag} {race['name']} ({'спринт'})\n{circuit_name} ({date})\n\n"
            )
        else:
            text += (
                    f"{race['round']}. {flag} {race['name']}\n{circuit_name} ({date})\n\n"
                )
    return text