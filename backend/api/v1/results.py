from ninja import Router
from typing import List, Optional
from pydantic import BaseModel
from services.race_service import get_relevant_race
from datetime import datetime
from core.models import GrandPrix
from services.utils import SESSION_MAP, PRACTICE_SESSIONS
from services.openf1_service import get_meeting_key, get_session_key
from services.race_service import get_race_by_round
from services.result_service import (
    get_practice_results,
    get_qualifying_results,
    get_race_results,
)


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


class PracticeResultSchema(BaseModel):
    position: int
    driver_code: str
    first_name: str
    last_name: str
    team_name: str
    flag: str
    time: str
    gap: str
    laps: int


class QualifyingResultSchema(BaseModel):
    position: int
    driver_code: str
    first_name: str
    last_name: str
    team_name: str
    flag: str
    segment: str
    time: str
    gap: str


class RaceResultSchema(BaseModel):
    position: int
    driver_code: str
    first_name: str
    last_name: str
    team_name: str
    flag: str
    points: int
    time: str
    gap: str
    laps: int


class ResultsResponseSchema(BaseModel):
    round: int
    race_name: str
    session: str
    results: List[dict]


@router.get("/relevant_race", response=RaceSchema)
async def get_relevant_race_api(request):
    """
    Получить релевантный Гран-при для отображения результатов
    """
    race = await get_relevant_race()
    
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


@router.get("/{round}/{session}", response=ResultsResponseSchema)
async def get_session_results_api(request, round, session):
    """
    Получить результаты сессии
    """
    race = await get_race_by_round(round)
    session_name = SESSION_MAP.get(session)
    meeting_key = await get_meeting_key(race.name, race.year)
    session_key = await get_session_key(meeting_key, session_name, race.year)

    if session in PRACTICE_SESSIONS:
        results_data = await get_practice_results(session_key)
    elif session == "qualifying" or session == "sprint_qualifying":
        results_data = await get_qualifying_results(session_key)
    else:
        results_data = await get_race_results(session_key)
    
    
    return ResultsResponseSchema(
        round=race.round,
        race_name=race.name,
        session=session,
        results=results_data,
    )