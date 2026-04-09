from django.utils import timezone
from datetime import timedelta
from core.models import GrandPrix
from loguru import logger


PRE_WEEKEND_WINDOW = timedelta(hours=12)
RACE_ACTIVE_WINDOW = timedelta(hours=4)

SPRINT_DURATION_HOURS = 2
RACE_DURATION_HOURS = 4


def get_relevant_race():
    """
    Возвращает релевантный Гран-при для отображения результатов.

    Логика:
    - за 12 часов до FP1 и до 4 часов после старта гонки считается,
      что уикенд активен → возвращается next_race
    - в остальное время возвращается последний завершившийся этап
    """
    now = timezone.now()

    next_race = (
        GrandPrix.objects
        .filter(race_datetime__gte=now - RACE_ACTIVE_WINDOW)
        .order_by("fp1_datetime")
        .first()
    )
    
    if next_race:

        start_window = next_race.fp1_datetime - PRE_WEEKEND_WINDOW
        end_window = next_race.race_datetime + RACE_ACTIVE_WINDOW

        if start_window <= now <= end_window:
            return next_race

    last_race = (
        GrandPrix.objects
        .filter(race_datetime__lt=now)
        .order_by("-race_datetime")
        .first()
    )

    if last_race is None:
        return None
    
    return last_race
    
    
def get_last_completed_race():
    """
    Возвращает последний Гран-при, у которого уже были начислены очки
    """
    now = timezone.now()
    
    next_race = GrandPrix.objects.filter(
        race_datetime__gte=now - timedelta(hours=RACE_DURATION_HOURS)
    ).order_by("race_datetime").first()

    last_race = GrandPrix.objects.filter(
        race_datetime__lt=now - timedelta(hours=RACE_DURATION_HOURS)
    ).order_by("-race_datetime").first()
    
    if not next_race and not last_race:
        return None, None
    
    if not next_race:
        return last_race, "Race"
    
    if next_race.has_sprint and next_race.sprint_datetime:
        sprint_end = next_race.sprint_datetime + timedelta(hours=SPRINT_DURATION_HOURS)
        if now >= sprint_end:
            return next_race, "Sprint"

    if now >= next_race.race_datetime + timedelta(hours=RACE_DURATION_HOURS):
        return next_race, "Race"
    
    return last_race, "Race"
