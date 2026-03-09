import fastf1
from pathlib import Path
from loguru import logger


CACHE_DIR = Path("fastf1_cache")

CACHE_DIR.mkdir(parents=True, exist_ok=True)

fastf1.Cache.enable_cache(CACHE_DIR)


SESSION_MAP = {
    "fp1_datetime": "FP1",
    "fp2_datetime": "FP2",
    "fp3_datetime": "FP3",
    "sprint_qualifying_datetime": "SQ",
    "sprint_datetime": "S",
    "qualifying_datetime": "Q",
    "race_datetime": "R"
}


def load_session(race, session_field):
    """
    Загружает сессию из FastF1
    """
    try:
        session_code = SESSION_MAP.get(session_field)

        if not session_code:
            raise ValueError(f"Неизвестная сессия: {session_field}")
        
        session = fastf1.get_session(
            race.year,
            race.round,
            session_code
        )
        session.load()

        return session
    except Exception as e:
        logger.error(
            f"Ошибка при загрузке сессии из FastF1:"
            f"year={race.year}, round={race.round}, session={session_field}"
        )
        raise e