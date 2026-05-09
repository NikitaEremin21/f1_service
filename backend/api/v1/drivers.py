from ninja import Router
from typing import List
from pydantic import BaseModel
from services.driver_service import get_drivers_list
from asgiref.sync import sync_to_async
from services.utils import DRIVER_FLAGS


router = Router()

class DriverSchema(BaseModel):
    number: int
    driver_code: str
    first_name: str
    last_name: str
    team: str
    flag: str


@router.get("/all", response=List[DriverSchema])
async def get_drivers_api(request):
    """
    Получить список пилотов
    """
    drivers = await sync_to_async(get_drivers_list)()
    result = []
    for driver in drivers:
        team_name = driver.team.name if driver.team else 'Нет команды'
        result.append(
            DriverSchema(
                number=driver.number,
                driver_code=driver.code,
                first_name=driver.first_name,
                last_name=driver.last_name,
                team=team_name,
                flag=DRIVER_FLAGS.get(driver.code, "")
            )
        )
    return result