from core.models import Driver
from services.utils import DRIVER_FLAGS


def format_drivers_list(drivers):
    text = f"Список пилотов формулы 1 сезон 2026 \n\n"
    text += "<pre>"
    for driver in drivers:
        flag = DRIVER_FLAGS.get(driver.code, "")
        text += f"{driver.number:>2} {flag} {driver.first_name} {driver.last_name} - {driver.team}\n"
    text += "</pre>"
    return text


def get_drivers_list():
    drivers_list = list(
        Driver.objects.select_related('team').all()
    )
    return drivers_list