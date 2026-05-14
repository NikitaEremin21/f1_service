from services.driver_service import get_drivers_list
from services.utils import DRIVER_FLAGS
from services.openf1_service import (
    get_results,
    get_driver
)
from asgiref.sync import sync_to_async


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

    drivers_list = await sync_to_async(get_drivers_list)()
    drivers = {driver.number: driver for driver in drivers_list}

    drivers_info = await get_driver(session_key)
    drivers_info_dict = {driver["driver_number"]: driver for driver in drivers_info} if drivers_info else {}

    best_time = None
    for result in session_data:
        duration = result.get('duration')
        if duration is not None:
            if best_time is None or duration < best_time:
                best_time = duration
    
    driver_results = []
    for result in session_data:
        driver_number = result.get("driver_number")
        position = result.get("position")
        duration = result.get("duration")
        gap = result.get("gap_to_leader")
        laps = result.get("number_of_laps", 0)
        
        driver = drivers.get(driver_number)
        
        if driver:
            driver_code = driver.code
            team_name = driver.team.name if driver.team else "-"
            flag = DRIVER_FLAGS.get(driver_code, "")
            first_name = driver.first_name
            last_name = driver.last_name
        else:
            driver_info = drivers_info_dict.get(driver_number)
            if driver_info:
                driver_code = driver_info.get("name_acronym", f"#{driver_number}")
                team_name = driver_info.get("team_name", "-")
                first_name = driver_info.get("first_name", "")
                last_name = driver_info.get("last_name", "")
            else:
                driver_code = f"#{driver_number}"
                team_name = "-"
                first_name = ""
                last_name = ""
            flag = DRIVER_FLAGS.get(driver_code, "")
        
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
            "driver_code": driver_code,
            "first_name": first_name,
            "last_name": last_name,
            "team_name": team_name,
            "flag": flag,
            "time": time_display,
            "gap": gap_display,
            "laps": laps,
        })
    
    driver_results.sort(key=lambda x: x["position"])
    return driver_results


async def get_qualifying_results(session_key):
    """
    Получает результаты квалификации для конкретного раунда и сессии
    """
    session_data = await get_results(session_key)
    results_by_number = {r['driver_number']: r for r in session_data}

    drivers_list = await sync_to_async(get_drivers_list)()

    pole_time = None
    pole_driver = None
    for result in session_data:
        if result.get('position') == 1:
            durations = result.get('duration', [])
            if len(durations) >= 3 and durations[2] is not None:
                pole_time = durations[2]
                pole_driver = result.get('driver_number')
                break

    driver_results = []
    for driver in drivers_list:
        driver_result = results_by_number.get(driver.number)

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
                if pole_time is not None and driver.number != pole_driver:
                    gap = display_time - pole_time
                    gap_display = f"+{gap:.3f}"
                else:
                    gap_display = "-"
            else:
                time_display = "No time"
                gap_display = "-"

            driver_results.append(
                {
                    "position": position,
                    "driver_code": driver.code,
                    "first_name": driver.first_name,
                    "last_name": driver.last_name,
                    "team_name": driver.team.name if driver.team else "-",
                    "flag": DRIVER_FLAGS.get(driver.code, ""),
                    "segment": segment,
                    "time": time_display,
                    "gap": gap_display,
                }
            )
        else:
            driver_results.append(
                {
                    "position": 999,
                    "driver_code": driver.code,
                    "first_name": driver.first_name,
                    "last_name": driver.last_name,
                    "team_name": driver.team.name if driver.team else "-",
                    "flag": DRIVER_FLAGS.get(driver.code, ""),
                    "segment": "Q1",
                    "time": "No time",
                    "gap": "-",
                }
            )
    driver_results.sort(key=lambda x: x["position"])
    return driver_results


async def get_race_results(session_key):
    """
    Получает результаты гонки или спринта для конкретного раунда и сессии
    """
    session_data = await get_results(session_key)
    results_by_number = {r['driver_number']: r for r in session_data}

    drivers_list = await sync_to_async(get_drivers_list)()

    driver_results = []
    for driver in drivers_list:
        driver_result = results_by_number.get(driver.number)

        if driver_result:
            position = driver_result.get("position")
            points = driver_result.get("points")
            gap = driver_result.get("gap_to_leader")
            
            if position == 1:
                gap_display = "-"
            elif isinstance(gap, (int, float)):
                gap_display = f"+{gap:.3f}"
                if gap == 0:
                    gap_display = "-"
            else:
                gap_display = str(gap)

            duration = driver_result.get("duration")
            if duration and position == 1:
                time_display = format_race_time_seconds(duration)
            else:
                time_display = gap_display

            driver_results.append(
                {
                    "position": position,
                    "driver_code": driver.code,
                    "first_name": driver.first_name,
                    "last_name": driver.last_name,
                    "team_name": driver.team.name if driver.team else "-",
                    "flag": DRIVER_FLAGS.get(driver.code, ""),
                    "points": int(points),
                    "time": time_display,
                    "gap": gap_display,
                    "laps": driver_result.get("number_of_laps", 0),
                }
            )
        else:
            driver_results.append(
                {
                    "position": 999,
                    "driver_code": driver.code,
                    "first_name": driver.first_name,
                    "last_name": driver.last_name,
                    "team_name": driver.team.name if driver.team else "-",
                    "flag": DRIVER_FLAGS.get(driver.code, ""),
                    "points": 0,
                    "time": "DNF",
                    "gap": "-",
                    "laps": 0,
                }
            )
    driver_results.sort(key=lambda x: x["position"])
    return driver_results
