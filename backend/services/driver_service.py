from core.models import Driver


def get_drivers_list():
    drivers_list = list(
        Driver.objects.select_related('team').all()
    )
    return drivers_list