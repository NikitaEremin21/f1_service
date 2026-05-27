from services.openf1_service import (
    get_meeting_key,
    get_session_key,
    get_championship_drivers,
    get_championship_teams,
)
from services.race_service import get_last_completed_race
from loguru import logger
from asgiref.sync import sync_to_async


async def get_drivers_standings():
    """
    Загружает зачет пилотов
    """
    try:
        race, session_name = await sync_to_async(get_last_completed_race)()

        if race is None:
            return 0, []

        race_name = race.name
        year = race.year
        meeting_key = await get_meeting_key(race_name, year)
        session_key = await get_session_key(meeting_key, session_name, year)
        championship_drivers = await get_championship_drivers(session_key)

        if not championship_drivers:
            return year, []

        return year, championship_drivers
    except AttributeError as e:
        logger.error(f"Ошибка атрибута при загрузке чемпионата пилотов: {e}")
        return 0, []
    except Exception as e:
        logger.error(f"Ошибка при загрузке чемпионата пилотов: {e}")
        return 0, []


async def get_teams_standings():
    """
    Загружает кубок конструкторов
    """
    try:
        race, session_name = await sync_to_async(get_last_completed_race)()

        if race is None:
            return 0, []

        race_name = race.name
        year = race.year
        meeting_key = await get_meeting_key(race_name, year)
        session_key = await get_session_key(meeting_key, session_name, year)
        championship_teams = await get_championship_teams(session_key)
    
        if not championship_teams:  
            return year, []
        
        return year, championship_teams
    except AttributeError as e:
        logger.error(f"Ошибка атрибута при загрузке кубка конструкторов: {e}")
        return 0, []
    except Exception as e:
        logger.error(f"Ошибка при загрузке кубка конструкторов: {e}")
        return 0, []

