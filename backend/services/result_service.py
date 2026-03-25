from core.models import GrandPrix, Driver
from services.fastf1_service import load_session
from math import isnan
from services.driver_service import get_drivers_list
from services.utils import (
    GP_FLAGS,
    DRIVER_FLAGS,
)
from services.openf1_service import (
    get_results,
    get_meeting_key,
    get_session_key,
    get_driver
)
import pandas as pd
from loguru import logger


PRACTICE_SESSIONS = [
    "fp1_datetime",
    "fp2_datetime",
    "fp3_datetime"
]


SESSION_MAP = {
    "fp1_datetime": "Practice 1",
    "fp2_datetime": "Practice 2",
    "fp3_datetime": "Practice 3",
    "sprint_qualifying_datetime": "Sprint Qualifying",
    "sprint_datetime": "Sprint",
    "qualifying_datetime": "Qualifying",
    "race_datetime": "Race"
}

def format_race_time_seconds(seconds):
    """
    Форматирует время гонки из секунд в "1:33:15.607"
    """
    if seconds is None:
        return "No time"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours}:{minutes:02d}:{secs:06.3f}"


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


def format_qualifying_time(seconds):
    """
    Форматирует время для квалификации 
    """
    if seconds is None:
        return "No time"
    
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"


def get_format_race_message_fast_f1(session, race):
    """
    Формирует результаты гонки / спринта, полученные из FastF1
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
                pos = "NC"
            
            elif "DSQ" in status:
                time_display = "DSQ"
                pos = "NC"

            elif "Did not start" in status:
                time_display = "DNS"
                pos = "NC"

            elif not pd.isna(time):
                time_display = f"+{format_timedelta(time)}"

            else:
                time_display = status

        text += f"{pos:>2}. {DRIVER_FLAGS.get(driver):<1} {driver:<4} {team:<16} {points:>3} {time_display:>11}\n"
        text += "-" * 45 + "\n"
    
    text += "</pre>"

    return text


def get_format_qualifying_message(session, race, session_field):
    """
    Формирует результаты квалификации
    """
    race_name = race.name
    
    drivers = get_drivers_list()
    
    results = {r['driver_number']: r for r in session}
    
    pole_time = None
    pole_driver = None
    for result in session:
        if result['position'] == 1:
            if len(result['duration']) >= 3 and result['duration'][2] is not None:
                pole_time = result['duration'][2]
                pole_driver = result['driver_number']
                break
    
    driver_data = []

    for driver in drivers:
        driver_number = driver.number
        driver_code = driver.code
        team_name = driver.team.name if driver.team else "-"
        
        result = results.get(driver_number)
        
        if result:
            durations = result['duration']
            pos = result['position']

            if pos <= 10:
                segment = "Q3"
                if len(durations) >= 3 and durations[2] is not None:
                    display_time = durations[2]
                else:
                    display_time = None
            elif pos <= 16:
                segment = "Q2"
                if len(durations) >= 2 and durations[1] is not None:
                    display_time = durations[1]
                else:
                    display_time = None
            else:
                segment = "Q1"
                if durations[0] is not None:
                    display_time = durations[0]
                else:
                    display_time = None
            
            if display_time is not None:
                time_display = format_qualifying_time(display_time)
                if pole_time is not None and driver_number != pole_driver:
                    gap = display_time - pole_time
                    gap_display = f"+{gap:.3f}"
                else:
                    gap_display = "-"
            else:
                time_display = "No time"
                gap_display = "-"
        else:
            time_display = "No time"
            segment = "Q1"
            gap_display = "-"
            pos = 999
        
        driver_data.append({
            "pos": pos,
            "driver": driver_code,
            "team": team_name,
            "flag": DRIVER_FLAGS.get(driver_code, ""),
            "segment": segment,
            "time": time_display,
            "gap": gap_display,
        })
    
    driver_data.sort(key=lambda x: x["pos"])
    
    text = f"{GP_FLAGS.get(race_name, '')} {race_name} {GP_FLAGS.get(race_name, '')}\n\n"
    text += "<pre>"
    text += f"{'Pos':<3} {'Driver':<6} {'Team':<12} {'Seg':<3} {'Time':<8} {'Gap':<6}\n"
    text += "-" * 43 + "\n"
    
    for r in driver_data:
        pos_display = "-" if r["pos"] == 999 else str(r["pos"])
        text += f"{pos_display:>2}. {r['flag']} {r['driver']:<3} {r['team']:<12} {r['segment']:<3} {r['time']:>8} {r['gap']:>6}\n"
    
    text += "</pre>"
    return text


def get_format_practice_message(race, session_key, session_field):
    """
    Формирует результаты свободных практик
    """
    race_name = race.name
    practice_name = SESSION_MAP.get(session_field)
    results = get_results(session_key)
    drivers_list = get_drivers_list()
    drivers = {driver.number: driver for driver in drivers_list}
    drivers_info_list = get_driver(session_key)
    drivers_info = {driver["driver_number"]: driver for driver in drivers_info_list}

    text = f"{GP_FLAGS.get(race_name, '')} {race_name} {GP_FLAGS.get(race_name, '')}\n\n"
    text += f"{practice_name}"
    text += "<pre>"
    text += f"{'Pos':<3} {'Driver':<6} {'Team':<12} {'Time':<8} {'Gap':<6} {'Laps':<4}\n"
    text += "-" * 45 + "\n"

    for result in results:
        position = result["position"]
        driver_number = result["driver_number"]
        duration = result["duration"]
        gap = result["gap_to_leader"]
        laps = result["number_of_laps"]
        

        if driver_number in drivers:
            driver = drivers[driver_number]
            driver_code = driver.code
            team_name = driver.team.name if driver.team else "-"
            flag = DRIVER_FLAGS.get(driver_code, "")
        else:
            driver = drivers_info.get(driver_number)
            driver_code = driver["name_acronym"]
            team_name = driver["team_name"]
            flag = DRIVER_FLAGS.get(driver_code, "")
        
        if duration is None:
            time_display = "No time"
            gap_display = "-"
        else:
            time_display = format_qualifying_time(duration)
            
            if position == 1 or gap == 0:
                gap_display = "-"
            else:
                gap_display = f"+{gap:.3f}"

        text += f"{position:>2}. {flag:} {driver_code:<3} {team_name:<12} {time_display:>8} {gap_display:>6} {laps:>4}\n"
        text += "-" * 45 + "\n"

    text += "</pre>"

    return text


def get_format_race_message(session, race, session_field):
    """
    Форматирует результаты спринта / гонки
    """
    race_name = race.name
    session_name = SESSION_MAP.get(session_field)

    drivers_list = get_drivers_list()

    results = {r['driver_number']: r for r in session}

    driver_data = []

    for driver in drivers_list:
        driver_number = driver.number
        driver_code = driver.code
        team_name = driver.team.name if driver.team else "-"
        flag = DRIVER_FLAGS.get(driver_code, "")

        result = results.get(driver_number)

        if result:
            position = result.get("position")
            points = result.get("points")
            gap = result.get("gap_to_leader")
            laps = result.get("number_of_laps", 0)

            if position == 1:
                gap_display = "-"
            elif isinstance(gap, (int, float)):
                gap_display = f"+{gap:.3f}"
            else:
                gap_display = str(gap)
            
            duration = result.get("duration")
            if duration and position == 1:
                time_display = format_race_time_seconds(duration)
            else:
                time_display = gap_display

            driver_data.append({
                "pos": position,
                "driver": driver_code,
                "team": team_name,
                "flag": flag,
                "points": int(points),
                "time": time_display,
                "gap": gap_display,
                "laps": laps,
            })
        else:
            driver_data.append({
                "pos": 999,
                "driver": driver_code,
                "team": team_name,
                "flag": flag,
                "points": 0,
                "time": "DNF",
                "gap": "-",
                "laps": 0,
            })

    driver_data.sort(key=lambda x: x["pos"])

    text = f"{GP_FLAGS.get(race_name)} {race_name} {GP_FLAGS.get(race_name)}\n\n"
    text += f"{session_name}\n"
    text += "<pre>"    
    text += f"{'Pos':<3} {'Driver':<6} {'Team':<12}  {'Pts':<3} {'Time':<11}\n"
    text += "-" * 40 + "\n"

    for r in driver_data:
        pos_display = "NC" if r["pos"] == 999 else str(r["pos"])
        text += f"{pos_display:>2}. {r['flag']} {r['driver']:<3} {r['team']:<12} {r['points']:>3}  {r['time']:>11}\n"

    text += "</pre>"
    
    return text


def get_session_results(round, session_field):
    """
    Загружает данные сессии и возвращает готовый текст с результатами
    """
    race = GrandPrix.objects.get(round=round)
    meeting_name = race.name
    session_name = SESSION_MAP.get(session_field)
    year = race.year

    meeting_key = get_meeting_key(meeting_name, year)
    session_key = get_session_key(meeting_key, session_name, year)

    if session_field in PRACTICE_SESSIONS:
        return get_format_practice_message(race, session_key, session_field)
    
    if session_field == "qualifying_datetime" or session_field == "sprint_qualifying_datetime":
        session = get_results(session_key)
        return get_format_qualifying_message(session, race, session_field)
    
    if session_field == "race_datetime" or session_field == "sprint_datetime":
        session = get_results(session_key)
        return get_format_race_message(session, race, session_field)