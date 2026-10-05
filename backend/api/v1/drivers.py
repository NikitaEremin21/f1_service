from ninja import Router
from typing import List
from pydantic import BaseModel
from services.driver_service import get_primary_drivers_list
from services.utils import DRIVER_FLAGS


router = Router()

class DriverSchema(BaseModel):
    number: int | None = None
    driver_code: str
    first_name: str
    last_name: str
    team: str
    flag: str


@router.get("/all", response=List[DriverSchema])
async def get_drivers_api(request):
    """
    Получить список основных пилотов.
    Допускается хранить в БД всех пилотов, но для этого API удобно отдавать только primary-пилотов.
    """
    drivers = await get_primary_drivers_list()
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
                flag=(driver.flag or DRIVER_FLAGS.get(driver.code, ""))
            )
        )
    return result