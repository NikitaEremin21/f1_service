from ninja import Router
from typing import List
from pydantic import BaseModel
from loguru import logger
from services.standing_service import (
    get_drivers_standings,
    get_teams_standings,
)
from services.driver_service import get_drivers_list
from services.utils import (
    DRIVER_FLAGS,
    TEAMS_FLAGS,
    TEAMS_DISPLAY_NAMES,
)


router = Router()


class DriversSchema(BaseModel):
    position: int
    flag: str
    driver_number: int
    first_name: str
    last_name: str
    team_name: str
    points: int


class DriverStandingSchema(BaseModel):
    year: int
    standings: List[DriversSchema]


class TeamsSchema(BaseModel):
    position: int
    flag: str
    team_name: str
    points: int


class TeamsStandingSchema(BaseModel):
    year: int
    standings: List[TeamsSchema]


@router.get("/drivers", response=DriverStandingSchema)
async def get_drivers_standings_api(request):
    """
    Получить зачет пилотов
    """
    year, standings_drivers = await get_drivers_standings()

    if not standings_drivers:
        return DriverStandingSchema(year=year, standings=[])
    
    drivers_list = await get_drivers_list()
    drivers_dict = {
        int(driver.number): driver for driver in drivers_list if driver.number is not None
    }
    drivers_by_code = {}
    for driver in drivers_list:
        if not driver.code:
            continue
        code = str(driver.code).upper()
        if code in drivers_by_code:
            logger.warning(f"Duplicate driver code in DB: {code} => {drivers_by_code[code].first_name} {drivers_by_code[code].last_name} and {driver.first_name} {driver.last_name}")
            current = drivers_by_code[code]
            pick = current if (current.is_primary and not driver.is_primary) else driver
            drivers_by_code[code] = pick
            continue
        drivers_by_code[code] = driver

    standings_list = []
    for standing in standings_drivers:
        driver_number_raw = standing.get("driver_number")
        driver_number = int(driver_number_raw) if driver_number_raw is not None else None
        driver_code = str(standing.get("driver_code", "")).upper() if standing.get("driver_code") else ""

        driver = drivers_dict.get(driver_number) if driver_number is not None else None
        if driver is None and driver_code:
            driver = drivers_by_code.get(driver_code)

        driver_flag = ""
        if driver:
            driver_flag = driver.flag or DRIVER_FLAGS.get(str(driver.code).upper(), "")

        standings_list.append(
            DriversSchema(
                position=standing.get("position_current", 0),
                flag=driver_flag,
                driver_number=driver_number if driver_number is not None else 0,
                first_name=driver.first_name if driver else "",
                last_name=driver.last_name if driver else "",
                team_name=driver.team.name if driver and driver.team else "-",
                points=standing.get("points_current", 0),
            )
        )

    standings_list.sort(key=lambda x: x.position)
    
    result = DriverStandingSchema(
        year=year,
        standings=standings_list
    )

    return result


@router.get("/constructors", response=TeamsStandingSchema)
async def get_constructors_standings_api(request):
    """
    Получить кубок конструкторов
    """
    year, standings_teams = await get_teams_standings()

    if not standings_teams:
        return TeamsStandingSchema(year=year, standings=[])
    
    standings_list = []
    for standing in standings_teams:
        api_team_name = standing.get("team_name", "")
        display_name = TEAMS_DISPLAY_NAMES.get(api_team_name, api_team_name)
        standings_list.append(
            TeamsSchema(
                position=standing.get("position_current", 0),
                flag=TEAMS_FLAGS.get(display_name),
                team_name=display_name,
                points=int(standing.get("points_current", 0)) if standing.get("points_current") is not None else 0,
            )
        )

    standings_list.sort(key=lambda x: x.position)

    result = TeamsStandingSchema(
        year=year,
        standings=standings_list
    )

    return result
