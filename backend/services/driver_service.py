from core.models import Driver


def format_drivers_list(drivers):
    text = f"Список пилотов формулы 1 сезон 2026 \n\n"
    for driver in drivers:
        text += f"{driver.number} - {driver.first_name} {driver.last_name} - {driver.team}\n"
    return text


def get_drivers_list():
    drivers_list = list(
        Driver.objects.select_related('team').all()
    )
    return drivers_list