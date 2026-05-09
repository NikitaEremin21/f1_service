from ninja import Router
from typing import List
from pydantic import BaseModel
from services.constructor_service import get_constructors_list
from asgiref.sync import sync_to_async
from services.utils import TEAMS_FLAGS


router = Router()


class ConstructorsSchema(BaseModel):
    name: str
    nationality: str
    flag: str


@router.get("/all", response=List[ConstructorsSchema])
async def get_constructors_api(request):
    """
    Получить список команд
    """
    constructors = await sync_to_async(get_constructors_list)()
    result = []
    for constructor in constructors:
        result.append(
            ConstructorsSchema(
                name=constructor.name,
                nationality=constructor.nationality,
                flag=TEAMS_FLAGS.get(constructor.name, "")
            )
        )

    return result