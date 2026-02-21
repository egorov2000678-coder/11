from aiogram.fsm.state import State, StatesGroup


class TransfersStates(StatesGroup):
    choosing_from = State()
    entering_to = State()
    entering_amount = State()
    entering_comment = State()
    confirming = State()
