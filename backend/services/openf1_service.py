from shlex import quote

from services.http_client import http_client
from services.cache.decorators import async_cache
import json
from loguru import logger


@async_cache(prefix="openf1:meeting_key", ttl=604800)
async def get_meeting_key(meeting_name, year):
    """
    Получает meeting_key
    """
    url = f"https://api.openf1.org/v1/meetings"
    meeting_name = meeting_name.replace("'", "")
    try:
        data = await http_client.get(
            url, params={
                "year": year,
                "meeting_name": meeting_name,
            }
        )
        
        if not data:
            return None
        
        meeting_key = data[0].get('meeting_key')
        return meeting_key
    except Exception as e:
        logger.warning(
            f"Ошибка при получении meeting_key для {meeting_name}"
        )
        raise e
    

@async_cache(prefix="openf1:session_key", ttl=604800)
async def get_session_key(meeting_key, session_name, year):
    """
    Получает session_key
    """
    url = f"https://api.openf1.org/v1/sessions"
    try:
        data = await http_client.get(
            url, params={
                "meeting_key": meeting_key,
                "session_name": session_name,
                "year": year,
            }
        )
        if not data:
            return None
        
        session_key = data[0].get('session_key')
        return session_key
    except Exception as e:
        logger.warning(
            f"Ошибка при получении session_key"
        )
        raise e
    

@async_cache(prefix="openf1:session_result", ttl=5400)
async def get_results(session_key):
    """
    Получает результаты сессии
    """
    url = f"https://api.openf1.org/v1/session_result"
    try:
        data = await http_client.get(
            url, params={
                "session_key": session_key,
                "position<=22": "",
            }
        )

        if not data:
            return None
        
        return data
    except Exception as e:
        logger.warning(
            f"Ошибка при получении session_key"
        )
        raise e
    

@async_cache(prefix="openf1:driver", ttl=5400)
async def get_driver(session_key):
    """
    Получает информацию о пилотах, участвовавших в сессии.
    """
    url = f"https://api.openf1.org/v1/drivers"
    try:
        data = await http_client.get(
            url, params={
                "session_key": session_key,
            }
        )
        if not data:
            return None
        

        return data
    except Exception as e:
        logger.warning(
            f"Ошибка при получении session_key"
        )
        raise e

    

@async_cache(prefix="openf1:championship_drivers", ttl=5400)  
async def get_championship_drivers(session_key):
    """
    Получает актуальный зачёт пилотов (чемпионат)
    """
    url = f"https://api.openf1.org/v1/championship_drivers"
    try:
        data = await http_client.get(
            url, params={
                "session_key": session_key,
            }
        )

        if not data:
            return None
        
        return data
    except Exception as e:
        logger.warning(
            f"Ошибка при загрузке турнирной таблицы пилотов из OpenF1"
        )
        raise e
    
    
@async_cache(prefix="openf1:championship_teams", ttl=5400)
async def get_championship_teams(session_key):
    """
    Получает актуальный зачёт конструкторов (кубок)
    """
    url = f"https://api.openf1.org/v1/championship_teams"
    try:
        data = await http_client.get(
            url, params={
                "session_key": session_key,
            }
        )

        if not data:
            return None
        
        return data
    except Exception as e:
        logger.warning(
            f"Ошибка при загрузке кубка конструкторов из OpenF1"
        )
        raise e
