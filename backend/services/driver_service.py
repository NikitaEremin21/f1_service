from core.models import Driver
from channels.db import database_sync_to_async


@database_sync_to_async
def get_drivers_list():
    drivers_list = list(
        Driver.objects
        .select_related('team')
        .order_by('team__name', 'number')
        .all()
    )
    return drivers_list