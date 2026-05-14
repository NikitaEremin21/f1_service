from services.utils import GP_FLAGS, SESSION_MAP


async def get_format_practice_message(data):
    """
    Форматирует результаты свободных практик
    """
    race_name = data.get("race_name")
    results = data.get("results")
    session_type = SESSION_MAP.get(data.get("session"))

    text = f"{GP_FLAGS.get(race_name, '')} {race_name} {GP_FLAGS.get(race_name, '')}\n\n"
    text += f"{session_type}\n"
    text += "<pre>"
    text += f"{'Pos':<3} {'Driver':<6} {'Team':<12} {'Time':<8} {'Gap':<6} {'Laps':<4}\n"
    text += "-" * 45 + "\n"

    for r in results:
        pos = r.get("position")
        flag = r.get("flag", "")
        driver_code = r.get("driver_code", "")
        team_name = r.get("team_name", "")[:12]
        time = r.get("time", "")
        gap = r.get("gap", "")
        laps = r.get("laps", 0)
        
        text += f"{pos:>2}. {flag} {driver_code:<3} {team_name:<12} {time:>8} {gap:>6} {laps:>4}\n"
    
    text += "</pre>"

    return text


async def get_format_qualifying_message(data):
    """
    Формирует результаты квалификации
    """
    race_name = data.get("race_name")
    results = data.get("results")
    session_type = SESSION_MAP.get(data.get("session"))

    text = f"{GP_FLAGS.get(race_name, '')} {race_name} {GP_FLAGS.get(race_name, '')}\n\n"
    text += f"{session_type}\n"
    text += "<pre>"
    text += f"{'Pos':<3} {'Driver':<6} {'Team':<12} {'Seg':<3} {'Time':<8} {'Gap':<6}\n"
    text += "-" * 43 + "\n"

    for result in results:
        pos = result.get("position")
        flag = result.get("flag", "  ")
        driver_code = result.get("driver_code")
        team_name = result.get("team_name")
        segment = result.get("segment")
        time = result.get("time")
        gap = result.get("gap")

        if pos == 999:
            pos_display = "-"
        else:
            pos_display = str(pos)

        text += f"{pos_display:>2}. {flag} {driver_code:<3} {team_name:<12} {segment:<3} {time:>8} {gap:>6}\n"
    
    text += "</pre>"
    
    return text


async def get_format_race_message(data):
    """
    Форматирует результаты гонки/спринта
    """
    race_name = data.get("race_name")
    results = data.get("results")
    session_type = SESSION_MAP.get(data.get("session"))

    text = f"{GP_FLAGS.get(race_name, '')} {race_name} {GP_FLAGS.get(race_name, '')}\n\n"
    text += f"{session_type}\n"
    text += "<pre>"
    text += f"{'Pos':<3} {'Driver':<6} {'Team':<12} {'Pts':<3} {'Time':<11}\n"
    text += "-" * 40 + "\n"
    
    for result in results:
        pos = result.get("position")
        if pos == 999:
            pos_display = "NC"
        else:
            pos_display = str(pos)
        
        flag = result.get("flag", "")
        driver_code = result.get("driver_code", "")
        team_name = result.get("team_name", "")[:12]
        points = result.get("points", 0)
        time = result.get("time", "")
        
        text += f"{pos_display:>2}. {flag} {driver_code:<3} {team_name:<12} {points:>3}  {time:>11}\n"
    
    text += "</pre>"

    return text

    
    