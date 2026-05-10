from ninja import Router
from typing import List
from pydantic import BaseModel
from services.standing_service import get_drivers_standings
from services.driver_service import get_drivers_list
from services.utils import DRIVER_FLAGS
from asgiref.sync import sync_to_async


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


@router.get("/drivers", response=DriverStandingSchema)
async def get_drivers_standings_api(request):
    """
    Получить зачет пилотов
    """
    year, standings_drivers = await get_drivers_standings()

    if not standings_drivers:
        return DriverStandingSchema(year=year, standings=[])
    
    drivers_list = await sync_to_async(get_drivers_list)()
    drivers_dict = {driver.number: driver for driver in drivers_list}

    standings_list = []
    for standing in standings_drivers:
        driver = drivers_dict.get(standing.get("driver_number"))
        standings_list.append(
            DriversSchema(
                        position=standing.get("position_current", 0),
                        flag=DRIVER_FLAGS.get(driver.code, "") if driver else "",
                        driver_number=standing.get("driver_number", 0),
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