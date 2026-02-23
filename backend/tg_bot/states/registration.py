from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    waiting_for_city = State()