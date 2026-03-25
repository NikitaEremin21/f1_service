from core.models import Constructor
from services.utils import TEAMS_FLAGS


def format_constructors_list(constructors):
    text = "Список команд формулы 1 сезон 2026: \n\n"
    text += "<pre>"
    for i, constructor in enumerate(constructors, 1):
        flag = TEAMS_FLAGS.get(constructor.name, "")
        text += f"{i:>2}. {constructor.name:<12} - {flag} {constructor.nationality}\n"
    text += "</pre>"
    return text


def get_constructors_list():
    constructors_list = list(
        Constructor.objects.all()
    )
    return constructors_list