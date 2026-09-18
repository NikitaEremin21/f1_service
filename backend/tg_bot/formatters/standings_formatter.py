def get_format_championship_drivers_message(championship_drivers):
    """
    Формирует таблицу чеспионата пилотов
    """
    year = championship_drivers.get("year", 0) 
    standings = championship_drivers.get("standings")
    text = f"Чемпионат формулы 1 {year}\n\n"
    text += "<pre>" 
    text += f"{'Pos':<3} {'Driver':<20} {'Team':<12} {'Pts':<3}\n"
    text += "-" * 41 + "\n"
    for dr in standings:
        position = dr.get("position", 0)
        flag = dr.get("flag", "")
        driver_number = dr.get("driver_number", "")
        first_name = dr.get("first_name", "")
        last_name = dr.get("last_name", "")
        team_name = dr.get("team_name", "-")
        points = dr.get("points", 0)

        initial = f"{first_name[0]}." if first_name else ""
        num_str = str(driver_number) if driver_number is not None else ""

        text += f"{position:>2}. {flag} {num_str:>2}  {initial:<1} {last_name:<10} {team_name:<12} {points:>3}\n"
    text += "</pre>"
    return text


def get_format_championship_teams_message(championship_teams):
    """
    Формирует таблицу чеспионата пилотов
    """
    year = championship_teams.get("year", 0)
    standings = championship_teams.get("standings")
    text = f"Чемпионат формулы 1 {year}\n\n"
    text += "<pre>"
    text += f"{'Pos':<3} {'Team':<18} {'Pts':<3}\n"
    text += "-" * 26 + "\n"
    for team in standings:
        position = team.get("position", 0)
        flag = team.get("flag", "")
        team_name = team.get("team_name", "-")
        points = team.get("points", 0)

        text += f"{position:>2}. {flag} {team_name:<15} {points:>3}\n"
    text += "</pre>" 
    return text
