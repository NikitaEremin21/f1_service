from core.models import Constructor
from channels.db import database_sync_to_async


@database_sync_to_async
def get_constructors_list():
    constructors_list = list(
        Constructor.objects.all()
    )
    return constructors_list