from core.models import Constructor


def format_constructors_list(constructors):
    text = "Список команд формулы 1 сезон 2026: \n\n"
    for i, constructor in enumerate(constructors, 1):
        text += f"{i}. {constructor.name} - {constructor.nationality}\n"
    return text


def get_constructors_list():
    constructors_list = list(
        Constructor.objects.all()
    )
    return constructors_list