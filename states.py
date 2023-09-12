from aiogram.fsm.state import StatesGroup, State


class SendId(StatesGroup):
    send_id = State()
    send_id_without_demo = State()
