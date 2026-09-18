from services.driver_service import get_drivers_list
from services.utils import DRIVER_FLAGS, TEAMS_DISPLAY_NAMES
from services.openf1_service import (
    get_results,
    get_driver
)
from loguru import logger


def _normalize_driver_number(value):
    """Приводит номер пилота к int, если возможно."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _get_driver_display_data(driver_number, drivers_by_number, drivers_info_dict):
    """
    Возвращает данные пилота для отображения.
    Принцип: OpenF1 даёт live-данные (номера, позиции, времена), а БД даёт справочные данные
    (имя, флаг, команда, статус). Если какие-то данные отсутствуют — подставляем безопасный fallback.
    """
    driver = drivers_by_number.get(_normalize_driver_number(driver_number))
    driver_info = drivers_info_dict.get(_normalize_driver_number(driver_number))

    if driver_info:
        driver_code = driver_info.get("name_acronym", f"#{driver_number}")
        team_name_raw = driver_info.get("team_name", "-")
        team_name = TEAMS_DISPLAY_NAMES.get(team_name_raw, team_name_raw)
        first_name = driver_info.get("first_name", "")
        last_name = driver_info.get("last_name", "")
        flag = driver.flag if driver and getattr(driver, 'flag', None) else DRIVER_FLAGS.get(driver_code, "")

        if not first_name and driver:
            first_name = driver.first_name
        if not last_name and driver:
            last_name = driver.last_name
        if not team_name or team_name == "-":
            team_name = driver.team.name if driver and driver.team else "-"

        return {
            "driver_code": driver_code,
            "team_name": team_name,
            "flag": flag,
            "first_name": first_name,
            "last_name": last_name,
        }

    if driver:
        driver_code = driver.code
        team_name_raw = driver.team.name if driver.team else "-"
        team_name = TEAMS_DISPLAY_NAMES.get(team_name_raw, team_name_raw)
        flag = driver.flag or DRIVER_FLAGS.get(str(driver_code).upper(), "")
        return {
            "driver_code": driver_code,
            "team_name": team_name,
            "flag": flag,
            "first_name": driver.first_name,
            "last_name": driver.last_name,
        }

    driver_code = f"#{driver_number}"
    return {
        "driver_code": driver_code,
        "team_name": "-",
        "flag": DRIVER_FLAGS.get(str(driver_code).upper(), ""),
        "first_name": "",
        "last_name": "",
    }


def format_qualifying_time(seconds):
    """
    Форматирует время для квалификации
    """
    if seconds is None:
        return "No time"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}:{secs:06.3f}"


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


async def get_practice_results(session_key):
    """
    Получает результаты свободных практик
    """
    session_data = await get_results(session_key)
    if not session_data:
        logger.warning(f"Нет данных практики для session_key={session_key}")
        return []

    drivers_list = await get_drivers_list()
    drivers_by_number = {_normalize_driver_number(driver.number): driver for driver in drivers_list}

    drivers_info = await get_driver(session_key)
    drivers_info_dict = {
        _normalize_driver_number(driver["driver_number"]): driver
        for driver in drivers_info
    } if drivers_info else {}

    best_time = None
    for result in session_data:
        duration = result.get('duration')
        if duration is not None:
            if best_time is None or duration < best_time:
                best_time = duration

    driver_results = []
    for result in session_data:
        driver_number = _normalize_driver_number(result.get("driver_number"))
        position = result.get("position")
        if position is None:
            position = 999
        duration = result.get("duration")
        gap = result.get("gap_to_leader")
        laps = result.get("number_of_laps", 0)

        driver_data = _get_driver_display_data(driver_number, drivers_by_number, drivers_info_dict)

        if duration is not None:
            time_display = format_qualifying_time(duration)
            if best_time is not None and duration != best_time:
                gap_display = f"+{duration - best_time:.3f}"
            else:
                gap_display = "-"
        else:
            time_display = "No time"
            gap_display = "-"

        driver_results.append({
            "position": position,
            "driver_code": driver_data["driver_code"],
            "first_name": driver_data["first_name"],
            "last_name": driver_data["last_name"],
            "team_name": driver_data["team_name"],
            "flag": driver_data["flag"],
            "time": time_display,
            "gap": gap_display,
            "laps": laps,
        })

    driver_results.sort(key=lambda x: (x.get("position") is None, x.get("position") if x.get("position") is not None else 9999))
    return driver_results


async def get_qualifying_results(session_key):
    """
    Получает результаты квалификации для конкретного раунда и сессии
    """
    session_data = await get_results(session_key)
    if not session_data:
        logger.warning(f"Нет данных квалификации для session_key={session_key}")
        return []

    drivers_list = await get_drivers_list()
    drivers_by_number = {_normalize_driver_number(driver.number): driver for driver in drivers_list}
    drivers_info = await get_driver(session_key)
    drivers_info_dict = {
        _normalize_driver_number(driver["driver_number"]): driver
        for driver in drivers_info
    } if drivers_info else {}

    results_by_number = {
        _normalize_driver_number(result['driver_number']): result
        for result in session_data
    }

    entrant_numbers = set(drivers_info_dict) | set(results_by_number)

    pole_time = None
    pole_driver = None
    for result in session_data:
        if result.get('position') == 1:
            durations = result.get('duration', [])
            if len(durations) >= 3 and durations[2] is not None:
                pole_time = durations[2]
                pole_driver = _normalize_driver_number(result.get('driver_number'))
                break

    driver_results = []
    for driver_number in sorted(entrant_numbers, key=lambda value: (value is None, value)):
        driver_result = results_by_number.get(driver_number)
        driver_data = _get_driver_display_data(driver_number, drivers_by_number, drivers_info_dict)

        if driver_result:
            durations = driver_result.get('duration', [])
            position = driver_result.get('position')

            if position <= 10:
                segment = "Q3"
                display_time = durations[2] if len(durations) >= 3 else None
            elif position <= 16:
                segment = "Q2"
                display_time = durations[1] if len(durations) >= 2 else None
            else:
                segment = "Q1"
                display_time = durations[0] if len(durations) >= 1 else None

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

            driver_results.append({
                "position": position,
                "driver_code": driver_data["driver_code"],
                "first_name": driver_data["first_name"],
                "last_name": driver_data["last_name"],
                "team_name": driver_data["team_name"],
                "flag": driver_data["flag"],
                "segment": segment,
                "time": time_display,
                "gap": gap_display,
            })
        else:
            driver_results.append({
                "position": 999,
                "driver_code": driver_data["driver_code"],
                "first_name": driver_data["first_name"],
                "last_name": driver_data["last_name"],
                "team_name": driver_data["team_name"],
                "flag": driver_data["flag"],
                "segment": "Q1",
                "time": "No time",
                "gap": "-",
            })

    driver_results.sort(key=lambda x: (x.get("position") is None, x.get("position") if x.get("position") is not None else 9999))
    return driver_results


async def get_race_results(session_key):
    """
    Получает результаты гонки или спринта для конкретного раунда и сессии
    """
    session_data = await get_results(session_key)
    if not session_data:
        logger.warning(f"Нет данных гонки для session_key={session_key}")
        return []

    drivers_list = await get_drivers_list()
    drivers_by_number = {_normalize_driver_number(driver.number): driver for driver in drivers_list}
    drivers_info = await get_driver(session_key)
    drivers_info_dict = {
        _normalize_driver_number(driver["driver_number"]): driver
        for driver in drivers_info
    } if drivers_info else {}

    results_by_number = {
        _normalize_driver_number(result['driver_number']): result
        for result in session_data
    }

    entrant_numbers = set(drivers_info_dict) | set(results_by_number)

    driver_results = []
    for driver_number in sorted(entrant_numbers, key=lambda value: (value is None, value if value is not None else -1)):
        driver_result = results_by_number.get(driver_number)
        driver_data = _get_driver_display_data(driver_number, drivers_by_number, drivers_info_dict)

        if driver_result:
            position = driver_result.get("position")
            if position is None:
                position = 999
            points = driver_result.get("points")
            gap = driver_result.get("gap_to_leader")

            if position == 1:
                gap_display = "-"
            elif isinstance(gap, (int, float)):
                gap_display = f"+{gap:.3f}"
                if gap == 0:
                    gap_display = "-"
            else:
                gap_display = "DNF" if gap is None else str(gap)

            duration = driver_result.get("duration")
            if duration and position == 1:
                time_display = format_race_time_seconds(duration)
            else:
                time_display = gap_display

            driver_results.append({
                "position": position,
                "driver_code": driver_data["driver_code"],
                "first_name": driver_data["first_name"],
                "last_name": driver_data["last_name"],
                "team_name": driver_data["team_name"],
                "flag": driver_data["flag"],
                "points": int(points) if points is not None else 0,
                "time": time_display,
                "gap": gap_display,
                "laps": driver_result.get("number_of_laps", 0),
            })
        else:
            driver_results.append({
                "position": 999,
                "driver_code": driver_data["driver_code"],
                "first_name": driver_data["first_name"],
                "last_name": driver_data["last_name"],
                "team_name": driver_data["team_name"],
                "flag": driver_data["flag"],
                "points": 0,
                "time": "DNF",
                "gap": "-",
                "laps": 0,
            })

    driver_results.sort(key=lambda x: (x.get("position") is None, x.get("position") if x.get("position") is not None else 9999))
    return driver_results