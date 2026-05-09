def format_constructors_message(constructors):
    text = "Список команд формулы 1 сезон 2026: \n\n"
    text += "<pre>"
    for i, constructor in enumerate(constructors, 1):
        name = constructor.get('name', 'team_name')
        nationality = constructor.get('nationality', '')
        flag = constructor.get('flag', '')
        text += f"{i:>2}. {name:<12} - {flag} {nationality}\n"
    text += "</pre>"
    return text