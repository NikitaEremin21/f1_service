from core.models import GrandPrix
from services.fastf1_service import load_session
from math import isnan
from services.utils import (
    GP_FLAGS,
    DRIVER_FLAGS
)
import pandas as pd

PRACTICE_SESSIONS = [
    "fp1_datetime",
    "fp2_datetime",
    "fp3_datetime"
]


def format_timedelta(td):
    """
    Превращает pandas Timedelta в формат F1
    """
    seconds = td.total_seconds()

    minutes = int(seconds // 60)
    seconds = seconds % 60

    return f"{minutes}:{seconds:06.3f}"


def format_race_time(td):
    """
    Формат времени победителя
    """
    seconds = td.total_seconds()

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60

    return f"{hours}:{minutes:02d}:{seconds:06.3f}"


def get_format_race_message(session, race):
    """
    Формирует результаты гонки / спринта
    """
    race_name = race.name
    results = session.results

    text = f"{GP_FLAGS.get(race_name)} {race_name} {GP_FLAGS.get(race_name)}\n\n"
    text += "<pre>"    
    text += f"{'Pos':<3} {'Driver':<7} {'Team':<16} {'Pts':<3} {'Time':<11}\n"
    text += "-" * 45 + "\n"

    for row in results.itertuples():
        pos = "-" if isnan(row.Position) else int(row.Position)
        driver = row.Abbreviation
        team = row.TeamName
        points = 0 if pd.isna(row.Points) else int(row.Points)
        status = row.Status
        time = row.Time

        if pos == 1 and not pd.isna(time):
            time_display = format_race_time(time)

        else:
            if "Lap" in status:
                time_display = "+1 Lap"

            elif "DNF" in status or "Retired" in status:
                time_display = "DNF"
            
            elif "DSQ" in status:
                time_display = "DSQ"

            elif "Did not start" in status:
                time_display = "DNS"

            elif not pd.isna(time):
                time_display = f"+{format_timedelta(time)}"

            else:
                time_display = status

        text += f"{pos:>2}. {DRIVER_FLAGS.get(driver):<1} {driver:<4} {team:<16} {points:>3} {time_display:>11}\n"
        text += "-" * 45 + "\n"
    
    text += "</pre>"

    return text


def get_session_results(round, session_field):
    """
    Загружает данные сессии и возвращает готовый текст с результатами
    """
    race = GrandPrix.objects.get(round=round)
    session = load_session(race, session_field)

    return get_format_race_message(session, race)