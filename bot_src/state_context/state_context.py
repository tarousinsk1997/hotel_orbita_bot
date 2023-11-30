from aiogram.fsm.state import State, StatesGroup

class BOOKING_TICKET_CLUB(StatesGroup):
    CHOOSE_EVENT = State()
    CHOOSE_TABLE = State()
    PRE_CHECKOUT_STATE = State()
    CHECK_PAY_EXISTS = State()


class CHECK_BOOK_ENTRY(StatesGroup):
    CHOOSE_ENTRY = State()

class REQUEST_CONTACT(StatesGroup):
    REQUEST_CONTACT = State()



class QR_VALIDATION(StatesGroup):
    CHOOSE_EVENT = State()
    CHOOSE_TABLE = State()
    PRE_CHECKOUT_STATE = State()
