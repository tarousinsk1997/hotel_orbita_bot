from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


import locale

from callback_handlers.callback_classes import MyCallback_rest, MyCallback_jazz_club, MyCallback_event_picker_left_right_arrow, \
      MyCallback_jazz_club_back, MyCallback_event_picker_event_picked, MyCallback_event_picker_event_picked_back, \
      MyCallback_table_picker, MyCallback_rest_back, MyCallback_table_picker_confirmed, MyCallback_successfull_payment_picker_left_right_arrow, \
      MyCallback_successfull_payment_get_qr_code

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


# Основная клавиатура разделов inline
inline_btn_1 = InlineKeyboardButton(text='🏡 Гостиница', callback_data='__')
inline_btn_2 = InlineKeyboardButton(text='🍗 Ресторан', callback_data=MyCallback_rest(button_descriptor='to_rest_main_kb').pack())
inline_btn_3 = InlineKeyboardButton(text='🎷 Орбита Джаз Клуб', callback_data=MyCallback_jazz_club(button_descriptor='to_club_main_kb').pack())
inline_kb_main = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_3], [inline_btn_1, inline_btn_2]])


inline_btn_main = InlineKeyboardButton(text='', callback_data='button1')


#Reply кнопка меню

reply_main_button = KeyboardButton(text='🏡Главное меню')
reply_main_markup = ReplyKeyboardMarkup(keyboard=[[reply_main_button]], resize_keyboard=True)


# раздел Ресторан 2

inline_btn_2_1 = InlineKeyboardButton(text='↩️ Назад', callback_data=MyCallback_jazz_club_back(button_descriptor='to_main_kb').pack())
inline_btn_2_2 = InlineKeyboardButton(text='🛒Бронирование места', callback_data=MyCallback_rest(button_descriptor='to_rest_booking').pack())
inline_btn_2_3 = InlineKeyboardButton(text='🍓Показать меню', callback_data=MyCallback_rest(button_descriptor='show_rest_links').pack())
inline_kb_2 = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_2_3], [inline_btn_2_1]])

#раздел меню ресторана 2.1

inline_btn_2_3_1 = InlineKeyboardButton(text='↩️ Назад', callback_data=MyCallback_rest_back(button_descriptor='to_rest_main_kb').pack())
inline_btn_2_3_2 = InlineKeyboardButton(text='🍕 Основное меню', url="https://telegra.ph/Menyu-restorana-Orbita-11-09")
inline_btn_2_3_3 = InlineKeyboardButton(text='🍷 Винная карта', url="https://telegra.ph/Vinnaya-karta-restorana-Orbita-11-09")
inline_btn_2_3_4 = InlineKeyboardButton(text='🍸 Меню Коктейлей', url="https://telegra.ph/Koktejli-11-18")
inline_kb_2_3 = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_2_3_2], [inline_btn_2_3_3, inline_btn_2_3_4], [inline_btn_2_3_1]])




# раздел Орбита Джаз 3

inline_btn_3_1 = InlineKeyboardButton(text='↩️ Назад', callback_data=MyCallback_jazz_club_back(button_descriptor='to_main_kb').pack())
inline_btn_3_2 = InlineKeyboardButton(text='Анонсированные мероприятия', callback_data=MyCallback_jazz_club(button_descriptor='to_event_review').pack())
inline_btn_3_3 = InlineKeyboardButton(text='Мои заявки бронирования', callback_data=MyCallback_jazz_club(button_descriptor='my_orders').pack())


inline_kb_3 = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_3_2], [inline_btn_3_3], [inline_btn_3_1]])


# раздел заявок бронирования
inline_btn_3_4_1 = InlineKeyboardButton(text='↩️ Назад', callback_data=MyCallback_jazz_club_back(button_descriptor='to_club_main_kb').pack())
inline_btn_3_4_2 = InlineKeyboardButton(text='🚮 Оплаченные (архивные)', callback_data=MyCallback_jazz_club(button_descriptor='archive_payment').pack())
inline_btn_3_4_4 = InlineKeyboardButton(text='✅ Оплаченные (активные)', callback_data=MyCallback_jazz_club(button_descriptor='successfull_payment').pack())
inline_btn_3_4_5 = InlineKeyboardButton(text='🗙 Отмена оплаченного бронирования', callback_data=MyCallback_jazz_club(button_descriptor='refund').pack())


inline_kb_3_4 = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_3_4_4], [inline_btn_3_4_2], [inline_btn_3_4_5], [inline_btn_3_4_1]])


#админ панель

inline_btn_admin_analytics = InlineKeyboardButton(text='🧮 Аналитика', callback_data='button_0_1')
inline_btn_admin_operator = InlineKeyboardButton(text='Оператор', callback_data='button_0_2')
inline_kb_admin = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_admin_analytics], [inline_btn_admin_operator]])



#режим валидации qr-кода operator_1

inline_btn_admin_operator_1 = InlineKeyboardButton(text='↩️ Назад', callback_data='button_0_2_1')
inline_btn_admin_operator_2 = InlineKeyboardButton(text='Режим Валидации QR', callback_data='button_0_2_2')
inline_kb_operator_validator = InlineKeyboardMarkup(inline_keyboard=[[inline_btn_admin_operator_1], [inline_btn_admin_operator_2]])





#создание клавиатуры выбора ивента для бронирования

def gen_event_picker_kb(event_URL, event_id) -> InlineKeyboardMarkup:
    button_URL = InlineKeyboardButton(text='Подробное описание мероприятия', url=event_URL)
    button_arrow_right = InlineKeyboardButton(text="➡", callback_data=MyCallback_event_picker_left_right_arrow(arrow_type='right').pack())
    button_arrow_left = InlineKeyboardButton(text="⬅", callback_data=MyCallback_event_picker_left_right_arrow(arrow_type='left').pack())
    button_choose_table = InlineKeyboardButton(text='Бронирование места', callback_data=MyCallback_event_picker_event_picked(valid=True, event_id=event_id).pack())
    button_back = InlineKeyboardButton(text="↩️ Назад", callback_data=MyCallback_jazz_club_back(button_descriptor='to_club_main_kb').pack())

    event_list_kb_markup = InlineKeyboardMarkup(inline_keyboard=[[button_URL],[button_arrow_left, button_arrow_right], [button_choose_table], [button_back]])
    return event_list_kb_markup


#создание клавиатуры выбора стола для бронирования

def gen_table_picker_kb(table_list, chosen_event_id) -> InlineKeyboardButton:
    keyboard_row = []
    keyboard_col = []
    col_counter = 0
    elem_counter = 0
    button_back = InlineKeyboardButton(text="↩️ Назад", callback_data=MyCallback_event_picker_event_picked_back(valid=True, event_id=chosen_event_id).pack())

    for elem in table_list:
        col_counter += 1
        button = InlineKeyboardButton(text=elem['Место'].replace('_', ' '), callback_data=MyCallback_table_picker(valid=True, seat=elem['Место'], event_id=chosen_event_id).pack())
        keyboard_col.append(button)
        if col_counter % 4 == 0:
            keyboard_col_copy = keyboard_col.copy()
            keyboard_row.append(keyboard_col_copy)
            keyboard_col.clear()
            col_counter = 0
        elem_counter += 1
        if elem_counter == len(table_list) and len(keyboard_col) != 0:
            keyboard_row.append(keyboard_col)

    keyboard_row.append([button_back])
    table_list_kb_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_row)
    return (table_list_kb_markup)


#Клавиатура Да/Нет

def get_yes_no_kb(seat, event_id) -> InlineKeyboardMarkup:
    
    button_yes = InlineKeyboardButton(text="Да", callback_data=MyCallback_table_picker_confirmed(confirmed=True, seat=seat, event_id=event_id).pack())
    button_no = InlineKeyboardButton(text="Нет", callback_data=MyCallback_table_picker_confirmed(confirmed=False, seat=seat, event_id=event_id).pack())
    yes_no_kb = InlineKeyboardMarkup(inline_keyboard=[[button_yes, button_no]])
    return yes_no_kb

#Клавиатура ссылок

def get_url_button_inline_markup(text:str, URL:str) ->InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, url=URL)]])
    return inline_markup


def get_success_payments_kb(QR_code, event_id, order_id):
    button_arrow_right = InlineKeyboardButton(text="➡", callback_data=MyCallback_successfull_payment_picker_left_right_arrow(arrow_type='right').pack())
    button_arrow_left = InlineKeyboardButton(text="⬅", callback_data=MyCallback_successfull_payment_picker_left_right_arrow(arrow_type='left').pack())
    button_get_qr = InlineKeyboardButton(text='Получить QR-код', callback_data=MyCallback_successfull_payment_get_qr_code(valid=True, qr_code=QR_code, event_id=event_id, order_id=order_id).pack())
    button_back = InlineKeyboardButton(text="↩️ Назад", callback_data=MyCallback_jazz_club_back(button_descriptor='my_orders').pack())

        
    inline_markup = InlineKeyboardMarkup(inline_keyboard=[[button_arrow_left, button_arrow_right], [button_get_qr], [button_back]])

    return inline_markup


def back_payments_inline_markup():
    back_button = InlineKeyboardButton(text="↩️ Назад", callback_data=MyCallback_jazz_club_back(button_descriptor='successfull_payment').pack())
    markup = InlineKeyboardMarkup(inline_keyboard=[[back_button]])
    return markup


def request_phone_kb():
    request_button_yes = KeyboardButton(text='📱Отправить номер телефона', request_contact=True)
    request_button_no = KeyboardButton(text='Не отправлять номер телефона')
    return ReplyKeyboardMarkup(keyboard=[[request_button_yes], [request_button_no]], one_time_keyboard=True, resize_keyboard=True)


def get_existing_order_check_keyboard(chosen_event_id, event_URL, seat):
    button_back = InlineKeyboardButton(text="↩️ Вернуться к списку столов", callback_data=MyCallback_event_picker_event_picked(valid=True, event_id=chosen_event_id).pack())
    button_pay_old = InlineKeyboardButton(text="Оплатить существующий ордер", url=event_URL)
    button_pay_new = InlineKeyboardButton(text="💵Оплатить новый ордер", callback_data=MyCallback_table_picker_confirmed(confirmed=True, seat=seat, event_id=chosen_event_id).pack())
    markup = InlineKeyboardMarkup(inline_keyboard=[[button_pay_new], [button_pay_old], [button_back]])
    return markup
