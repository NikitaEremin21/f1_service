from aiogram import Router
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from datetime import datetime, timedelta
import loguru
from core.models import GrandPrix


router = Router()


def format_date(date):
    month_map = {
        'Jan': 'янв', 'Feb': 'фев', 'Mar': 'мар', 'Apr': 'апр',
        'May': 'май', 'Jun': 'июн', 'Jul': 'июл', 'Aug': 'авг',
        'Sep': 'сен', 'Oct': 'окт', 'Nov': 'ноя', 'Dec': 'дек'
    }
    start = date - timedelta(days=2)
    start_date = f"{start.day} {month_map.get(start.strftime('%b'), start.strftime('%b'))}"
    end_date = f"{date.day} {month_map.get(date.strftime('%b'), date.strftime('%b'))}"
    return f"{start_date} - {end_date}"


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


@router.message(Command("calendar"))
async def calendar_function(message):
    try:
        data = await sync_to_async(
            lambda: list(
                GrandPrix.objects.select_related('circuit').order_by('round').all()
            )
        )()
        calendar_text = get_calendar_message(data)
        await message.answer(calendar_text)
    except Exception as e:
        loguru.logger.error(f'Ошибка при получении календаря: {e}')
        await message.answer('Ошибка при получении календаря')