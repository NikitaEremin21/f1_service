import re
from datetime import datetime

from services.http_client import http_client
from services.cache.decorators import async_cache
from loguru import logger


def _normalize_meeting_name(value):
    """Нормализует название события для сравнения."""
    if value is None:
        return ""
    value = value.replace("'", "").replace("’", "").strip().lower()
    return re.sub(r"\s+", " ", value)


def _get_meeting_sort_key(item):
    """Возвращает ключ сортировки для выбора актуального события."""
    date_value = item.get("date_start") or item.get("date_end") or "1970-01-01T00:00:00+00:00"
    try:
        parsed = datetime.fromisoformat(date_value.replace("Z", "+00:00"))
    except ValueError:
        parsed = datetime.min
    return parsed, int(item.get("meeting_key") or 0)


@async_cache(prefix="openf1:meeting_key", ttl=604800)
async def get_meeting_key(meeting_name, year):
    """
    Получает meeting_key.

    OpenF1 может хранить несколько событий с одинаковым meeting_name в одном году
    (например, перенесённый GP с тем же названием). В таких случаях нужно выбирать
    актуальный, неотменённый и самый свежий по дате начала.
    """
    url = f"https://api.openf1.org/v1/meetings"
    normalized_name = _normalize_meeting_name(meeting_name)
    if not normalized_name:
        return None

    try:
        data = await http_client.get(
            url,
            params={
                "year": year,
            }
        )

        if not data:
            return None

        matches = []
        for item in data:
            if _normalize_meeting_name(item.get("meeting_name")) == normalized_name:
                matches.append(item)

        if not matches:
            return None

        preferred = [item for item in matches if not item.get("is_cancelled")]
        if preferred:
            matches = preferred

        return max(matches, key=_get_meeting_sort_key).get("meeting_key")

    except Exception:
        logger.exception(
            f"Ошибка при получении meeting_key для {meeting_name}"
        )
        raise
    

@async_cache(prefix="openf1:session_key", ttl=604800)
async def get_session_key(meeting_key, session_name, year):
    """
    Получает session_key
    """
    url = f"https://api.openf1.org/v1/sessions"
    try:
        data = await http_client.get(
            url,
            params={
                "meeting_key": meeting_key,
                "session_name": session_name,
                "year": year,
            }
        )
        if not data:
            return None
        
        return data[0].get('session_key')

    except Exception as e:
        logger.exception(
            f"Ошибка при получении session_key"
        )
        raise
    

@async_cache(prefix="openf1:session_result", ttl=12600)
async def get_results(session_key):
    """
    Получает результаты сессии
    """
    url = f"https://api.openf1.org/v1/session_result"
    try:
        data = await http_client.get(
            url, 
            params={
                "session_key": session_key,
                "position<=22": "",
            }
        )

        if not data:
            return None
        
        return data
    except Exception as e:
        logger.exception(
            f"Ошибка при получении session_key"
        )
        raise
    

@async_cache(prefix="openf1:driver", ttl=12600)
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
        logger.exception(
            f"Ошибка при получении информации о пилотах"
        )
        raise

    

@async_cache(prefix="openf1:championship_drivers", ttl=12600)  
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
        logger.exception(
            f"Ошибка при загрузке турнирной таблицы пилотов из OpenF1"
        )
        raise
    
    
@async_cache(prefix="openf1:championship_teams", ttl=12600)
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
        logger.exception(
            f"Ошибка при загрузке кубка конструкторов из OpenF1"
        )
        raise
