from services.driver_service import get_drivers_list
from services.openf1_service import (
    get_meeting_key,
    get_session_key,
    get_championship_drivers,
    get_championship_teams,
)
from services.utils import (
    DRIVER_FLAGS
)
from services.race_service import get_last_completed_race
from services.utils import TEAMS_FLAGS
from loguru import logger
from asgiref.sync import sync_to_async


def get_format_championship_drivers_message(race, championship_drivers):
    """
    Формирует таблицу чеспионата пилотов
    """
    drivers_list = get_drivers_list()
    drivers = {driver.number: driver for driver in drivers_list}


    text = f"Чемпионат формулы 1 {race.year}\n\n"
    text += "<pre>" 
    text += f"{'Pos':<3} {'Driver':<20} {'Team':<12} {'Pts':<3}\n"
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


async def get_drivers_standings():
    """
    Загружает зачет пилотов
    """
    try:
        race, session_name = await sync_to_async(get_last_completed_race)()

        if race is None:
            return "Чемпионат еще не начался.\n\nПосле первой гонки здесь появится таблица."

        race_name = race.name
        year = race.year
        meeting_key = await get_meeting_key(race_name, year)
        session_key = await get_session_key(meeting_key, session_name, year)
        championship_drivers = await get_championship_drivers(session_key)

        if not championship_drivers:
            return "Данные чемпионата временно недоступны."
        
        drivers_message = await sync_to_async(get_format_championship_drivers_message)(race, championship_drivers)
        return drivers_message
    except AttributeError as e:
        logger.error(f"Ошибка атрибута при загрузке чемпионата пилотов: {e}")
        return "🏁 Чемпионат пилотов временно недоступен.\n\nВозможно, сезон еще не начался."
    except Exception as e:
        logger.error(f"Ошибка при загрузке чемпионата пилотов: {e}")
        return "Чемпионат пилотов временно недоступен.\n\nВозможно, сезон еще не начался."



def get_format_championship_teams_message(race, championship_drivers):
    """
    Формирует таблицу чеспионата пилотов
    """
    text = f"Чемпионат формулы 1 {race.year}\n\n"
    text += "<pre>"
    text += f"{'Pos':<3} {'Team':<18} {'Pts':<3}\n"
    text += "-" * 26 + "\n"

    for team in championship_drivers:
        position = team["position_current"]
        team_name = team["team_name"]
        points_raw = team["points_current"]
        flag = TEAMS_FLAGS.get(team_name, "")
        points = int(points_raw) if points_raw is not None else 0

        text += f"{position:>2}. {flag} {team_name:<15} {points:>3}\n"

    text += "</pre>" 
    return text

async def get_teams_standings():
    """
    Загружает кубок конструкторов
    """
    try:
        race, session_name = await sync_to_async(get_last_completed_race)()

        if race is None:
            return "Кубок конструкторов еще не начался.\n\nПосле первой гонки здесь появится таблица."

        race_name = race.name
        year = race.year
        meeting_key = await get_meeting_key(race_name, year)
        session_key = await get_session_key(meeting_key, session_name, year)
        championship_teams = await get_championship_teams(session_key)

        if not championship_teams:
            return "Данные кубка конструкторов временно недоступны."
        
        teams_message = await sync_to_async(get_format_championship_teams_message)(race, championship_teams)
        return teams_message
    except AttributeError as e:
        logger.error(f"Ошибка атрибута при загрузке кубка конструкторов: {e}")
        return "Кубок конструкторов временно недоступен.\n\nВозможно, сезон еще не начался."
    except Exception as e:
        logger.error(f"Ошибка при загрузке кубка конструкторов: {e}")
        return "Кубок конструкторов временно недоступен.\n\nВозможно, сезон еще не начался."

