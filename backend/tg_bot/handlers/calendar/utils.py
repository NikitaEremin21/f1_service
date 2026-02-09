from datetime import timedelta


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