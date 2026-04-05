from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class MainMenuButtons:
    
    CALENDAR = "Календарь"
    UPCOMING_RACES = "Оставшиеся гонки"
    NEXT_RACE = "Следующая гонка"
    DRIVERS_LIST = "Список пилотов"
    TEAMS_LIST = "Список команд"
    RESULTS = "Результаты"
    TEAMS_STANDINGS = "Чемпионат команд"
    DRIVERS_STANDINGS = "Чемпионат пилотов"
    SETTINGS = "Настройки"

    
def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=MainMenuButtons.CALENDAR))
    builder.add(KeyboardButton(text=MainMenuButtons.UPCOMING_RACES))
    builder.add(KeyboardButton(text=MainMenuButtons.NEXT_RACE))
    builder.add(KeyboardButton(text=MainMenuButtons.DRIVERS_LIST))
    builder.add(KeyboardButton(text=MainMenuButtons.TEAMS_LIST))
    builder.add(KeyboardButton(text=MainMenuButtons.RESULTS))
    builder.add(KeyboardButton(text=MainMenuButtons.TEAMS_STANDINGS))
    builder.add(KeyboardButton(text=MainMenuButtons.DRIVERS_STANDINGS))
    # builder.add(KeyboardButton(text=MainMenuButtons.SETTINGS))

    builder.adjust(2, 2, 2, 2)

    return builder.as_markup(resize_keyboard=True)


