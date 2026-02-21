from aiogram.fsm.state import State, StatesGroup


class CardIssueStates(StatesGroup):
    entering_holder_name = State()
