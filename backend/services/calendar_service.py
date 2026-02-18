from datetime import datetime, timedelta
from django.utils import timezone
from core.models import GrandPrix
from services.utils import format_date


def get_calendar_message(data):
    text = f"Календарь формулы 1 2026\n\n"
    for gp in data:
        date = format_date(gp.date)
        if gp.has_sprint:
            text += (
                f"{gp.round}. {gp.name} ({'спринт'})\n{gp.circuit.name} ({date})\n\n"
            )
        else:
            text += (
                    f"{gp.round}. {gp.name}\n{gp.circuit.name} ({date})\n\n"
                )
    return text


def get_all_races():
    data = list(
        GrandPrix.objects.select_related('circuit').order_by('round').all()
    )
    return data


def get_upcoming_races():
    data = list(
        GrandPrix.objects.select_related('circuit')
        .filter(date__gte=timezone.now().date())
        .order_by('round').all()
    )
    return data