from core.models import Constructor


def get_constructors_list():
    constructors_list = list(
        Constructor.objects.all()
    )
    return constructors_list