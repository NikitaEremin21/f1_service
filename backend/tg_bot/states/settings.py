from aiogram.fsm.state import StatesGroup, State


class SettingsCity(StatesGroup):
    waiting_for_new_city = State()