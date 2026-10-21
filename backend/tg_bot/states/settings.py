from aiogram.fsm.state import StatesGroup, State


class SettingsCity(StatesGroup):
    waiting_for_new_city = State()


class Feedback(StatesGroup):
    waiting_for_message = State()


class SupportStars(StatesGroup):
    waiting_for_amount = State()