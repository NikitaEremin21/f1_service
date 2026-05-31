from ninja import Router
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from services.calendar_service import (
    get_all_races,
    get_upcoming_races,
    get_next_race_data,
)


router = Router()


class GrandPrixSchema(BaseModel):
    round: int
    name: str
    circuit_name: str
    circuit_location: str
    circuit_country: str
    date: date
    has_sprint: bool
    race_datetime: Optional[datetime] = None


class SessionSchema(BaseModel):
    name: str
    datetime: str
    local_datetime: str


class NextRaceSchema(BaseModel):
    round: int
    name: str
    circuit_name: str
    date: str
    has_sprint: bool
    sessions: List[SessionSchema]
    


@router.get("/all", response=List[GrandPrixSchema])
async def get_calendar_api(request):
    """
    Получить календарь гонок
    """
    races = await get_all_races()

    result = []
    for race in races:
        result.append(
            GrandPrixSchema(
                round=race.round,
                name=race.name,
                circuit_name=race.circuit.name,
                circuit_location=race.circuit.location,
                circuit_country=race.circuit.country,
                date=race.date,
                has_sprint=race.has_sprint,
                race_datetime=race.race_datetime
            )
        )

    return result


@router.get("/upcoming", response=List[GrandPrixSchema])
async def get_upcoming_races_api(request):
    """
    Получить календарь гонок
    """
    races = await get_upcoming_races()

    result = []
    for race in races:
        result.append(
            GrandPrixSchema(
                round=race.round,
                name=race.name,
                circuit_name=race.circuit.name,
                circuit_location=race.circuit.location,
                circuit_country=race.circuit.country,
                date=race.date,
                has_sprint=race.has_sprint,
                race_datetime=race.race_datetime
            )
        )

    return result


@router.get("/next_race", response=NextRaceSchema)
async def get_next_race_api(request, user_tz):
    """
    Получить информацию о следующей гонке
    """
    next_race = await get_next_race_data(user_tz)
    
    return next_race
