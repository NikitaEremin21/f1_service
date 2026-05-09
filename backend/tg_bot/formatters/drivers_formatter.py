def format_drivers_message(drivers):
    """
    Форматирует список пилотов для отправки в Telegram
    """
    text = f"Список пилотов формулы 1 сезон 2026 \n\n"
    text += "<pre>"
    for driver in drivers:
        number = driver.get("number", "")
        flag = driver.get("flag", "")
        first_name = driver.get("first_name", "")
        last_name = driver.get("last_name", "")
        team = driver.get("team", "Нет команды")
        text += f"{number:>2} {flag} {first_name} {last_name} - {team}\n"
    text += "</pre>"
    return text