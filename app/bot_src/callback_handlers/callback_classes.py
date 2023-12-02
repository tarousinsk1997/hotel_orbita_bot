from aiogram.filters.callback_data import CallbackData

class MyCallback_rest(CallbackData, prefix="restaurant"):
    button_descriptor: str


class MyCallback_rest_back(CallbackData, prefix="restaurant_back"):
    button_descriptor: str 


class MyCallback_jazz_club(CallbackData, prefix="club"):
    button_descriptor: str


class MyCallback_jazz_club_back(CallbackData, prefix="club_back"):
    button_descriptor: str


class MyCallback_event_picker_left_right_arrow(CallbackData, prefix="event_choose_arrow"):
    arrow_type: str


class MyCallback_event_picker_event_picked(CallbackData, prefix="event_picked"):
    valid: bool
    event_id: str


class MyCallback_event_picker_event_picked_back(CallbackData, prefix="event_picked_back"):
    valid: bool
    event_id: str


class MyCallback_table_picker(CallbackData, prefix="seat_picked"):
    valid: bool
    seat: str
    event_id: str


class MyCallback_table_picker_confirmed(CallbackData, prefix="seat_confirmed"):
    confirmed: bool
    seat: str
    event_id: str


class MyCallback_successfull_payment_picker_left_right_arrow(CallbackData, prefix="suc_pay_choose_arrow"):
    arrow_type: str

class MyCallback_successfull_payment_get_qr_code(CallbackData, prefix="qet_qr"):
    valid: bool
    event_id: str
    order_id:str
    qr_code: str

