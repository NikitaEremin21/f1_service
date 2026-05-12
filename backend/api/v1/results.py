from ninja import Router
from typing import List, Optional
from pydantic import BaseModel
from asgiref.sync import sync_to_async
from services.race_service import get_relevant_race
from datetime import datetime


router = Router()


class RaceSchema(BaseModel):
    round: int
    name: str
    has_sprint: bool
    fp1_datetime: Optional[datetime] = None
    fp2_datetime: Optional[datetime] = None
    fp3_datetime: Optional[datetime] = None
    sprint_qualifying_datetime: Optional[datetime] = None
    sprint_datetime: Optional[datetime] = None
    qualifying_datetime: Optional[datetime] = None
    race_datetime: Optional[datetime] = None


@router.get("/relevant_race", response=RaceSchema)
async def get_relevant_race_api(request):
    """
    Получить релевантный Гран-при для отображения результатов
    """
    race = await sync_to_async(get_relevant_race)()
    
    if not race:
        return None
    
    return RaceSchema(
        round=race.round,
        name=race.name,
        has_sprint=race.has_sprint,
        fp1_datetime=race.fp1_datetime,
        fp2_datetime=race.fp2_datetime,
        fp3_datetime=race.fp3_datetime,
        sprint_qualifying_datetime=race.sprint_qualifying_datetime,
        sprint_datetime=race.sprint_datetime,
        qualifying_datetime=race.qualifying_datetime,
        race_datetime=race.race_datetime
    )
