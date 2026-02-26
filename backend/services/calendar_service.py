from datetime import datetime, timedelta
from django.utils import timezone
from core.models import GrandPrix
from zoneinfo import ZoneInfo
from collections import defaultdict
from services.utils import format_date
from services.user_service import get_user_by_telegram_id


SESSION_LABELS = {
    "fp1_datetime": "FP1",
    "fp2_datetime": "FP2",
    "fp3_datetime": "FP3",
    "sprint_qualifying_datetime": "SQ",
    "sprint_datetime": "Sprint",
    "qualifying_datetime": "Q",
    "race_datetime": "R",
}


def get_calendar_message(data):
    """
    Формирует сообщение календаря
    """
    text = f"Календарь формулы 1 2026\n\n"
    for gp in data:
        date = format_date(gp.date)
        if gp.has_sprint:
            text += (
                f"{gp.round}. {gp.name} ({'спринт'})\n{gp.circuit.name} ({date})\n\n"
            )
        else:
            text += (
                    f"{gp.round}. {gp.name}\n{gp.circuit.name} ({date})\n\n"
                )
    return text


def group_sessions_by_local_day(sessions, user_tz):
    """
    Групперует сессии и преобразует в timezone пользователя
    """
    sessions_by_day = defaultdict(list)
    for field, dt in sessions:
        local_dt = dt.astimezone(ZoneInfo(user_tz))
        day_key = local_dt.date()
        sessions_by_day[day_key].append((field, local_dt))

    for day in sessions_by_day:
        sessions_by_day[day].sort(key=lambda x: x[1])

    return dict(sorted(sessions_by_day.items()))


def get_next_race_message(next_gp, sessions):
    """
    Формирует сообщение о следующей гонке
    """
    text = (f'🏁 Round {next_gp.round} - {next_gp.name}\n'
            f'{next_gp.circuit}\n\n')
    
    for day, session_list in sessions.items():
        dt_sample = session_list[0][1]
        weekday = dt_sample.strftime("%A")
        date_str = dt_sample.strftime("%d %B")
        text += f'{weekday} - {date_str}\n'

        for field, dt in session_list:
            session_name = SESSION_LABELS.get(field, field)
            time = dt.strftime("%H:%M")
            text += f'   {session_name} - {time}\n'
    return text


def get_all_races():
    """
    Возвращает из базы данных все гонки
    """
    data = list(
        GrandPrix.objects.select_related('circuit').order_by('round').all()
    )
    return data


def get_upcoming_races():
    """
    Возвращает из базы данных все гонки, которые еще не прошли
    """
    data = list(
        GrandPrix.objects.select_related('circuit')
        .filter(date__gte=timezone.now().date())
        .order_by('round').all()
    )
    return data


def get_next_race(user_id):
    """
    Возвращает информацию о следующей гонке
    """
    user_tz = get_user_by_telegram_id(user_id).timezone
    next_gp = GrandPrix.objects.select_related('circuit').filter(
        race_datetime__gte=timezone.now()
    ).order_by('race_datetime').first()
    if not next_gp:
        return 'Сезон закончен или следующая гонка еще не определена'
    
    sessions = []
    if next_gp.has_sprint:
        for field in ["fp1_datetime", "sprint_qualifying_datetime", "sprint_datetime",
                      "qualifying_datetime", "race_datetime"]:
            dt = getattr(next_gp, field)
            if dt:
                sessions.append((field, dt))
    else:
        for field in ["fp1_datetime", "fp2_datetime", "fp3_datetime",
                      "qualifying_datetime", "race_datetime"]:
            dt = getattr(next_gp, field)
            if dt:
                sessions.append((field, dt))
    
    sessions_by_day = group_sessions_by_local_day(sessions, user_tz)
    next_race_message = get_next_race_message(next_gp, sessions_by_day)
    
    return next_race_message