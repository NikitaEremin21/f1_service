from core.models import Driver
from channels.db import database_sync_to_async


@database_sync_to_async
def get_drivers_list():
    drivers_list = list(
        Driver.objects.select_related('team').all()
    )
    return drivers_list