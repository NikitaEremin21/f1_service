from datetime import datetime, timedelta
from collections import defaultdict
from services.utils import (
    format_date,
    GP_FLAGS,
)


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


def group_sessions_by_local_day(sessions):
    """
    Групперует сессии и преобразует в timezone пользователя
    """
    sessions_by_day = defaultdict(list)

    for session in sessions:
        local_dt = datetime.fromisoformat(session['local_datetime'])
        day_key = local_dt.date()
        sessions_by_day[day_key].append((session['name'], local_dt))

    for day in sessions_by_day:
        sessions_by_day[day].sort(key=lambda x: x[1])

    return dict(sorted(sessions_by_day.items()))


def get_next_race_message(next_race_data):
    """
    Формирует сообщение о следующей гонке
    """
    if not next_race_data:
        return "Сезон завершен. Следите за новостями о следующем сезоне!"
    
    flag = GP_FLAGS.get(next_race_data['name'], "")
    text = (f'Round {next_race_data["round"]} - {flag} {next_race_data["name"]}\n'
            f'{next_race_data["circuit_name"]}\n\n')
    
    sessions_by_day = group_sessions_by_local_day(next_race_data['sessions'])
    
    for day, session_list in sessions_by_day.items():
        first_session_name, first_session_time = session_list[0]
        weekday = first_session_time.strftime("%A")
        date_str = first_session_time.strftime("%d %B")
        text += f'{weekday} - {date_str}\n'

        for session_name, session_time in session_list:
            time_str = session_time.strftime("%H:%M")
            text += f'   {session_name} - {time_str}\n'

    return text