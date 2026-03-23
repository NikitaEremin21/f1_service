from services.driver_service import get_drivers_list
from services.openf1_service import (
    get_meeting_key,
    get_session_key,
    get_championship_drivers,
)
from services.utils import (
    DRIVER_FLAGS
)
from services.race_service import get_last_completed_race


def get_format_championship_drivers_message(race, championship_drivers):
    """
    Формирует таблицу чеспионата пилотов
    """
    drivers_list = get_drivers_list()
    drivers = {driver.number: driver for driver in drivers_list}


    text = f"Чемпионат формулы 1 {race.year}\n\n"
    text += "<pre>" 
    text += f"{'Pos':<3} {'Driver':<19} {'Team':<12} {'Pts':<3}\n"
    text += "-" * 41 + "\n"
    for dr in championship_drivers:
        position = dr["position_current"]
        driver_number = dr["driver_number"]
        points_raw = dr["points_current"]
        points = int(points_raw) if points_raw is not None else 0
        driver = drivers.get(driver_number)
        driver_code = driver.code
        first_name = driver.first_name
        last_name = driver.last_name
        team_name = driver.team.name if driver.team else "-"
        flag = DRIVER_FLAGS.get(driver_code, "")
        text += f"{position:>2}. {flag} {driver_number:>2}  {first_name[0]}. {last_name:<10} {team_name:<12} {points:>3}\n"
    text += "</pre>"
    return text


def get_drivers_standings():
    """
    Загружает зачет пилотов
    """
    race, session_name = get_last_completed_race()
    race_name = race.name
    year = race.year
    meeting_key = get_meeting_key(race_name, year)
    session_key = get_session_key(meeting_key, session_name, year)
    championship_drivers = get_championship_drivers(session_key)
    drivers_message = get_format_championship_drivers_message(race, championship_drivers)
    return drivers_message
