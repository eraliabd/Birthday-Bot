from aiogram.dispatcher.filters.state import State, StatesGroup


class RegisterState(StatesGroup):
    first_name = State()
    last_name = State()
    date_of_birth = State()
    image = State()
