from django.utils import timezone
from core.models import GrandPrix
from zoneinfo import ZoneInfo


SESSION_LABELS = {
    "fp1_datetime": "FP1",
    "fp2_datetime": "FP2",
    "fp3_datetime": "FP3",
    "sprint_qualifying_datetime": "SQ",
    "sprint_datetime": "Sprint",
    "qualifying_datetime": "Q",
    "race_datetime": "R",
}


def get_all_races():
    """
    Возвращает из базы данных все гонки
    """
    data = list(
        GrandPrix.objects.select_related('circuit').order_by('round').all()
    )
    return data


def get_upcoming_races():
    """
    Возвращает из базы данных все гонки, которые еще не прошли
    """
    data = list(
        GrandPrix.objects.select_related('circuit')
        .filter(date__gte=timezone.now().date())
        .order_by('round').all()
    )
    return data


def get_next_race():
    next_gp = GrandPrix.objects.select_related('circuit').filter(
        race_datetime__gte=timezone.now()
    ).order_by('race_datetime').first()
    return next_gp


def get_next_race_data(user_tz):
    """
    Возвращает информацию о следующей гонке для API
    """
    next_gp = get_next_race()
    if not next_gp:
        return None
    
    sessions = []
    if next_gp.has_sprint:
        session_fields = ["fp1_datetime", "sprint_qualifying_datetime", "sprint_datetime",
                          "qualifying_datetime", "race_datetime"]
    else:
        session_fields = ["fp1_datetime", "fp2_datetime", "fp3_datetime",
                          "qualifying_datetime", "race_datetime"]
    
    for field in session_fields:
        dt = getattr(next_gp, field)
        if dt:
            sessions.append({
                "name": SESSION_LABELS.get(field, field),
                "datetime": dt.isoformat(),
                "local_datetime": dt.astimezone(ZoneInfo(user_tz)).isoformat(),
            })
    
    return {
        'round': next_gp.round,
        'name': next_gp.name,
        'circuit_name': next_gp.circuit.name,
        'date': next_gp.date.isoformat(),
        'has_sprint': next_gp.has_sprint,
        'sessions': sessions,
    }