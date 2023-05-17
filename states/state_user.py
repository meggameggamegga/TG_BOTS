from aiogram.dispatcher.filters.state import State,StatesGroup


class AlertState(StatesGroup):
    alert = State()
    time = State()
    change_time = State()
    change_alert = State()