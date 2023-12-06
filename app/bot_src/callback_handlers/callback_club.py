from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest

import qrcode
import io
from datetime import datetime
from bot_src import misc
from yoomoney import Quickpay

from natsort import natsorted
from bot_src.state_context.state_context import CHECK_BOOK_ENTRY, BOOKING_TICKET_CLUB
from bot_src.standard_answers import basic_answer_vars
from bot_src.scheduled_tasks import update_awaiting_orders_list
from bot_src.API import database_api
from bot_src.API import OneC_api
from bot_src.keyboards import keyboards as kb


from bot_src.callback_handlers.callback_classes import  MyCallback_jazz_club, MyCallback_event_picker_left_right_arrow, \
      MyCallback_jazz_club_back, MyCallback_event_picker_event_picked, MyCallback_event_picker_event_picked_back, \
      MyCallback_table_picker,  MyCallback_table_picker_confirmed, MyCallback_successfull_payment_picker_left_right_arrow, \
      MyCallback_successfull_payment_get_qr_code

from bot_src.event_handlers.base_answer_function import send_edit_message_callback, send_edit_photo_callback



router_club = Router()
from bot_src.bot_init import bot


test_payment_mode = '1'

event_date_str_representation = '%d.%m.%Y %H:%M'

async def convert_date_representation(oneC_date_string):
    return datetime.strptime(oneC_date_string, OneC_api.format_date_str).strftime(event_date_str_representation)


async def show_successful_payments_list(callback, state, is_last_message):

    if not await is_booking_server_available(callback, is_last_message):
        return
    
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass

    memory_data = await state.get_data()
    
    try:
        payment_data = memory_data['payment_data']
    except KeyError:
        payment_data = await OneC_api.get_book_entry_by_id(callback.from_user.id)

        if len(payment_data) == 0:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await send_edit_message_callback(callback, basic_answer_vars.no_successful_entries_answer, reply_markup=kb.inline_kb_3, is_last_message=is_last_message)
            #await bot.send_message( callback.from_user.id, basic_answer_vars.no_successful_entries_answer, reply_markup=kb.inline_kb_3)
            await bot.answer_callback_query(callback.id)

        
        await state.update_data({'payment_data': payment_data})
        
    

    current_operation_index = 0
    operation_to_pick = payment_data[current_operation_index]

    event_name = operation_to_pick['event_name'] 
    event_date = await convert_date_representation(operation_to_pick['event_date'])
    order_id = operation_to_pick['order_id']
    event_id = operation_to_pick['event_id'] 
    seat = operation_to_pick['table'].replace("_", " ")
    QR_code = operation_to_pick['QR']

    await state.update_data({'current_operation_index': current_operation_index}, )

    await send_edit_message_callback(callback, 
                                     f'''Оплаченный ордер:\n# order {event_id}:{order_id}\n\n\n{event_name}\n\n\nДата и время проведения:
                                    \n{event_date}\n\nЗабронированное место: {seat}''', 
                            is_last_message=is_last_message, 
                            reply_markup=kb.get_success_payments_kb(QR_code, event_id, order_id))
    #await bot.send_message(callback.from_user.id, f"Оплаченный ордер:\n\n# order {event_id}:{order_id}\n\n{event_name}\n\nДата и время проведения:\n\n{event_date}\n\n Забронированное место:\n\n{seat}", reply_markup=kb.get_success_payments_kb(QR_code, event_id, order_id))
    await state.set_state(CHECK_BOOK_ENTRY.CHOOSE_ENTRY)
    await bot.answer_callback_query(callback.id)


async def get_table_set_club(event_id, paste_mode:str, callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    """
    метод получения списка свободных столов
    """

    
    if not await is_booking_server_available(callback, is_last_message):
        return
    
    await state.set_state(BOOKING_TICKET_CLUB.CHOOSE_TABLE)

    event_data = await OneC_api.get_event_data()

    
    if len(event_data) == 0:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await send_edit_message_callback(callback, is_last_message=is_last_message, text=basic_answer_vars.no_events_available_answer, reply_markup=kb.inline_kb_3)
        #await bot.send_message(callback.from_user.id, basic_answer_vars.no_events_available_answer, reply_markup=kb.inline_kb_3)
        await bot.answer_callback_query(callback.id)
        return
        


    chosen_event_id = event_id
    await state.update_data({'chosen_event_id': chosen_event_id})
    event = [event for event in event_data if event['event_id'] == chosen_event_id][0]
    event_date = await convert_date_representation(event['event_date'])
    chosen_event_name_date = f"{event['event_name']}\n\nДата и время проведения:\n\n{event_date}"

    current_table_configuration = await OneC_api.get_table_configuration_data(chosen_event_id)

    await state.update_data({'current_table_configuration': current_table_configuration})


    #tables_not_booked = [elem for elem in current_table_configuration if "Стол" in elem['Место'] and elem['СтатусБронирования'] == 'Свободно']
    tables_not_booked = [elem for elem in current_table_configuration if elem['Место'] and elem['СтатусБронирования'] == 'Свободно']
    #tables_not_booked = sorted(tables_not_booked, key= lambda x: x['Место'])
    tables_not_booked = natsorted(tables_not_booked, key= lambda x: x['Место'])

    photo_string = "AgACAgIAAxkBAAIBrGVP5GT5p4CQse5AeF86R4TNrkwQAAL1zjEb-v6BSk3QFDsePqmGAQADAgADeQADMwQ"
    if paste_mode == 'edit':
        await send_edit_photo_callback(callback, media=photo_string, edit_content='media', caption = '',is_last_message=is_last_message, send_mode=paste_mode)
        await send_edit_photo_callback(callback, media=photo_string, 
                                       edit_content='caption', 
                                       caption=chosen_event_name_date, 
                                       is_last_message=is_last_message,
                                       send_mode=paste_mode, 
                                       reply_markup=kb.gen_table_picker_kb(tables_not_booked, chosen_event_id))
        #await bot.edit_message_media(media=media_photo, chat_id=callback.from_user.id, message_id=callback.message.message_id)
        #await bot.edit_message_caption(callback.from_user.id, callback.message.message_id, caption=chosen_event_name_date, reply_markup=kb.gen_table_picker_kb(tables_not_booked, chosen_event_id))
    elif paste_mode == 'send': 
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
        await send_edit_photo_callback(callback,
                                    media=photo_string, 
                                    send_mode=paste_mode, 
                                    edit_content='caption', 
                                    caption=chosen_event_name_date, 
                                    reply_markup=kb.gen_table_picker_kb(tables_not_booked, chosen_event_id))
        #await bot.send_photo(callback.from_user.id,  photo=photo_string, caption=chosen_event_name_date, reply_markup=kb.gen_table_picker_kb(tables_not_booked, chosen_event_id))

    await bot.answer_callback_query(callback.id) 



@router_club.callback_query(MyCallback_jazz_club.filter(F.button_descriptor =='to_club_main_kb'))
async def to_club_main(callback: CallbackQuery, is_last_message:bool): 
    
    await send_edit_message_callback(callback, basic_answer_vars.default_jazz_club_menu_answer, send_mode='edit', reply_markup=kb.inline_kb_3, is_last_message=is_last_message)
    #await bot.edit_message_text(basic_answer_vars.default_jazz_club_menu_answer, callback.from_user.id, callback.message.message_id, reply_markup=kb.inline_kb_3) 
    await bot.answer_callback_query(callback.id)



@router_club.callback_query(MyCallback_jazz_club_back.filter(F.button_descriptor =='to_club_main_kb'))
async def back_to_club_main(callback: CallbackQuery, is_last_message:bool):
    
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)  
    except TelegramBadRequest:
        pass
    await send_edit_message_callback(callback, basic_answer_vars.default_jazz_club_menu_answer, is_last_message=is_last_message, reply_markup=kb.inline_kb_3)
    #await bot.send_message(callback.from_user.id, basic_answer_vars.default_jazz_club_menu_answer, reply_markup=kb.inline_kb_3) 
    await bot.answer_callback_query(callback.id)


@router_club.callback_query(MyCallback_jazz_club_back.filter(F.button_descriptor =='to_main_kb'))
async def back_to_main_kb(callback: CallbackQuery, is_last_message:bool):
    await send_edit_message_callback(callback, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main, send_mode='edit', is_last_message=is_last_message)
    #await bot.edit_message_text(basic_answer_vars.default_main_menu_answer, callback.from_user.id, callback.message.message_id,  reply_markup=kb.inline_kb_main) 
    await bot.answer_callback_query(callback.id)   



@router_club.callback_query(MyCallback_jazz_club.filter(F.button_descriptor =='my_orders'))
async def to_orders_kb(callback: CallbackQuery, is_last_message:bool):
    await send_edit_message_callback(callback, basic_answer_vars.default_orders_menu_answer, reply_markup=kb.inline_kb_3_4, is_last_message=is_last_message, send_mode='edit')
    #await bot.edit_message_text("Раздел заявок бронирования", callback.from_user.id, callback.message.message_id , reply_markup=kb.inline_kb_3_4) 
    await bot.answer_callback_query(callback.id)     


@router_club.callback_query(MyCallback_jazz_club_back.filter(F.button_descriptor =='my_orders'))
async def back_to_orders_kb(callback: CallbackQuery, is_last_message:bool):
    await send_edit_message_callback(callback, basic_answer_vars.default_orders_menu_answer, reply_markup=kb.inline_kb_3_4, is_last_message=is_last_message, send_mode='edit')
    #await bot.edit_message_text("Раздел заявок бронирования", callback.from_user.id, callback.message.message_id , reply_markup=kb.inline_kb_3_4) 
    await bot.answer_callback_query(callback.id)    



@router_club.callback_query(MyCallback_jazz_club.filter(F.button_descriptor =='successfull_payment'))
async def to_successful_payments(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    await show_successful_payments_list(callback, state, is_last_message)




@router_club.callback_query(CHECK_BOOK_ENTRY.CHOOSE_ENTRY, MyCallback_jazz_club_back.filter(F.button_descriptor =='successfull_payment'))
async def back_to_successful_payments(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
        await show_successful_payments_list(callback, state, is_last_message)



@router_club.callback_query(MyCallback_jazz_club_back.filter(F.button_descriptor =='successfull_payment'))
async def back_to_successful_payments_no_state(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass

    await send_edit_message_callback(callback, basic_answer_vars.session_expired, is_last_message=is_last_message)
    await send_edit_message_callback(callback, basic_answer_vars.default_main_menu_answer, is_last_message=is_last_message, reply_markup=kb.inline_kb_main)
    #await bot.send_message(callback.from_user.id, basic_answer_vars.session_expired)
    #await bot.send_message(callback.from_user.id, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await bot.answer_callback_query(callback.id)

    

@router_club.callback_query(CHECK_BOOK_ENTRY.CHOOSE_ENTRY, MyCallback_successfull_payment_picker_left_right_arrow.filter(F.arrow_type.in_(['left', 'right'])))
async def operation_picker_arrow(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    
    if not await is_booking_server_available(callback, is_last_message):
        return
    
    memory_data = await state.get_data()
    try:
        payment_data = memory_data['payment_data']
        if 'right' in callback.data:
            current_operation_index = memory_data['current_operation_index'] + 1
        elif 'left' in callback.data:
            current_operation_index = memory_data['current_operation_index'] - 1
        
    except KeyError:
        payment_data = await OneC_api.get_book_entry_by_id(callback.from_user.id)
        
        current_operation_index = 0

        await state.update_data({'payment_data' : payment_data})


    try:
        operation_to_pick = payment_data[current_operation_index]
    except IndexError:
        current_operation_index = 0
        operation_to_pick = payment_data[current_operation_index]


    event_name = operation_to_pick['event_name'] 
    event_date = await convert_date_representation(operation_to_pick['event_date'])
    order_id = operation_to_pick['order_id']
    event_id = operation_to_pick['event_id'] 
    seat = operation_to_pick['table'].replace("_", " ")
    QR_code = operation_to_pick['QR']
    await state.update_data({'current_operation_index': current_operation_index})
    await send_edit_message_callback(callback, text=f'''Оплаченный ордер:\n# order {event_id}:{order_id}\n\n\n{event_name}\n\n\nДата и время проведения:
                                    \n{event_date}\n\nЗабронированное место: {seat}''', 
                                     send_mode='edit', reply_markup=kb.get_success_payments_kb(QR_code, event_id, order_id),
                                     is_last_message=is_last_message)
    #await bot.edit_message_text(f"Оплаченный ордер:\n\n# order {event_id}:{order_id}\n\n{event_name}\n\nДата и время проведения:\n\n{event_date}\n\n Забронированное место:\n\n{seat}", callback.from_user.id, callback.message.message_id, reply_markup=kb.get_success_payments_kb(QR_code, event_id, order_id))
    await bot.answer_callback_query(callback.id)


@router_club.callback_query(MyCallback_successfull_payment_picker_left_right_arrow.filter(F.arrow_type.in_(['left', 'right'])))
async def operation_picker_arrow_no_state(callback: CallbackQuery, state: FSMContext, is_last_message:bool):

    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except:
        pass
    await send_edit_message_callback(callback, basic_answer_vars.session_expired, is_last_message=is_last_message)
    await send_edit_message_callback(callback,  basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main, is_last_message=is_last_message)
    #await bot.send_message(callback.from_user.id, basic_answer_vars.session_expired)
    #await bot.send_message(callback.from_user.id, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await bot.answer_callback_query(callback.id)


@router_club.callback_query(MyCallback_jazz_club.filter(F.button_descriptor =='to_event_review'))
async def to_event_review(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    if not await is_booking_server_available(callback, is_last_message):
        return

    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass

    await state.set_state(BOOKING_TICKET_CLUB.CHOOSE_EVENT)
    memory_data = await state.get_data()
    try: 
        event_data = memory_data['event_data']
    except KeyError:
        event_data = await OneC_api.get_event_data()

        
        if len(event_data) == 0:
            await send_edit_message_callback(callback, basic_answer_vars.no_events_available_answer, reply_markup=kb.inline_kb_3, send_mode='edit', is_last_message=is_last_message)
            #await bot.edit_message_text(basic_answer_vars.no_events_available_answer, callback.from_user.id, callback.message.message_id, reply_markup=kb.inline_kb_3)
            await bot.answer_callback_query(callback.id)
            return
        

        
        await state.update_data({'event_data': event_data})
    

    current_event_index = 0
    event_to_pick = event_data[current_event_index]

    event_name = event_to_pick['event_name'] 
    event_URL = event_to_pick['event_URL']
    event_date = await convert_date_representation(event_to_pick['event_date'])
    photo_url = event_to_pick['event_photoURL']
    event_id = event_to_pick['event_id']
    await state.update_data({'current_event_index' : current_event_index})

    await send_edit_photo_callback(callback,
                                   media=photo_url,
                                   caption=f"{event_name}\n\n Дата и время проведения:\n\n{event_date}",
                                   reply_markup=kb.gen_event_picker_kb(event_URL, event_id),
                                   send_mode='send',
                                   is_last_message=is_last_message
                                   )

    #await bot.send_photo(callback.from_user.id, photo_url, caption=f"{event_name}\n\n Дата и время проведения:\n\n{event_date}", reply_markup=kb.gen_event_picker_kb(event_URL, event_id))
    await bot.answer_callback_query(callback.id)     


@router_club.callback_query(BOOKING_TICKET_CLUB.CHOOSE_TABLE, MyCallback_event_picker_event_picked_back.filter(F.valid ==True))
async def back_to_event_review(callback: CallbackQuery, state: FSMContext, is_last_message:bool):

    if not await is_booking_server_available(callback, is_last_message):
        return

    memory_data = await state.get_data()
    try:
        event_data = memory_data['event_data']
    except KeyError:
        event_data = await OneC_api.get_event_data()
               
        if len(event_data) == 0:
            await send_edit_message_callback(callback, basic_answer_vars.no_events_available_answer, reply_markup=kb.inline_kb_3, send_mode='edit', is_last_message=is_last_message)
            #await bot.edit_message_text(basic_answer_vars.no_events_available_answer, callback.from_user.id, callback.message.message_id, reply_markup=kb.inline_kb_3)
            await bot.answer_callback_query(callback.id)
            return
    
        await state.update_data({'event_data': event_data})


    current_event_index = 0
    event_to_pick = event_data[current_event_index]

    event_name = event_to_pick['event_name'] 
    event_URL = event_to_pick['event_URL']
    event_date = await convert_date_representation(event_to_pick['event_date'])
    photo_url = event_to_pick['event_photoURL']
    event_id = event_to_pick['event_id']
    await state.update_data({'current_event_index': current_event_index})
    await state.set_state(BOOKING_TICKET_CLUB.CHOOSE_EVENT)


    await send_edit_photo_callback(callback, photo_url, edit_content='media', send_mode='edit', caption = '')
    await send_edit_photo_callback(callback, '', edit_content='caption', send_mode='edit', caption=f"{event_name}\n\nДата и время проведения:\n\n{event_date}", 
                                   reply_markup=kb.gen_event_picker_kb(event_URL, event_id),
                                   is_last_message=is_last_message)
    
    #await bot.edit_message_media(InputMediaPhoto(media=photo_url), callback.from_user.id, callback.message.message_id)
    #await bot.edit_message_caption(callback.from_user.id, callback.message.message_id, caption=f"{event_name}\n\nДата и время проведения:\n\n{event_date}", reply_markup=kb.gen_event_picker_kb(event_URL, event_id))
   
    await bot.answer_callback_query(callback.id)  

@router_club.callback_query(BOOKING_TICKET_CLUB.CHOOSE_EVENT, MyCallback_event_picker_left_right_arrow.filter(F.arrow_type.in_(['left', 'right'])))
async def event_picker_arrow(callback: CallbackQuery, state: FSMContext, is_last_message:bool):

    if not await is_booking_server_available(callback, is_last_message):
        return
    
    memory_data = await state.get_data()
    try:
        event_data = memory_data['event_data']
        if 'right' in callback.data:
            current_event_index = memory_data['current_event_index'] + 1
        elif 'left' in callback.data:
            current_event_index = memory_data['current_event_index'] - 1
        
    except KeyError:
        event_data = await OneC_api.get_event_data()
        

        await state.update_data({'event_data': event_data})
        current_event_index = 0


    try:
        event_to_pick = event_data[current_event_index]
    except IndexError:
        current_event_index = 0
        event_to_pick = event_data[current_event_index]

    event_name = event_to_pick['event_name'] 
    event_URL = event_to_pick['event_URL']
    event_date = await convert_date_representation(event_to_pick['event_date'])
    photo_url = event_to_pick['event_photoURL']
    event_id = event_to_pick['event_id']

 
    await state.update_data({'current_event_index': current_event_index})    

    await send_edit_photo_callback(callback, media=photo_url, edit_content='media', send_mode='edit', caption='')
    await send_edit_photo_callback(callback, '', edit_content='caption', send_mode='edit', caption=f"{event_name}\n\nДата и время проведения:\n\n{event_date}", 
                                   reply_markup=kb.gen_event_picker_kb(event_URL, event_id),
                                   is_last_message=is_last_message)

    #await bot.edit_message_media(InputMediaPhoto(media=photo_url), callback.from_user.id, callback.message.message_id, event_id)
    #await bot.edit_message_caption(callback.from_user.id, callback.message.message_id, caption=f"{event_name}\n\nДата и время проведения:\n\n{event_date}", reply_markup=kb.gen_event_picker_kb(event_URL, event_id))


@router_club.callback_query(MyCallback_event_picker_left_right_arrow.filter(F.arrow_type.in_(['left', 'right'])))
async def event_picker_arrow_no_state(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass

    await send_edit_message_callback(callback, basic_answer_vars.session_expired, is_last_message=is_last_message)
    await send_edit_message_callback(callback,  basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main, is_last_message=is_last_message)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.session_expired)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await bot.answer_callback_query(callback.id)

    await bot.answer_callback_query(callback.id) 


@router_club.callback_query(BOOKING_TICKET_CLUB.CHOOSE_EVENT, MyCallback_event_picker_event_picked.filter(F.valid == True))
async def get_free_table_set_club(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    chosen_event_id = callback.data.split(":")[2]
    await get_table_set_club(event_id=chosen_event_id, paste_mode='edit', callback=callback, state=state, is_last_message=is_last_message)



@router_club.callback_query(BOOKING_TICKET_CLUB.CHOOSE_TABLE, MyCallback_table_picker.filter(F.valid == True))
async def pre_checkout_validation_club(callback: CallbackQuery, state: FSMContext, is_last_message:bool):

    if not await is_booking_server_available(callback, is_last_message):
        return
    
    await state.set_state(BOOKING_TICKET_CLUB.PRE_CHECKOUT_STATE)
    memory_data = await state.get_data()
    
    try:
        event_data = memory_data['event_data']
    except KeyError:
        event_data = await OneC_api.get_event_data()



    callback_data_split = callback.data.split(":")
    seat= callback_data_split[2]  
    event_id= callback_data_split[3]
    event = [event for event in event_data if event['event_id'] == event_id][0]
    event_date = await convert_date_representation(event['event_date'])
    chosen_event_name_date = f"{event['event_name']}\n\nДата и время проведения:\n\n{event_date}"
    seat_text = seat.replace("_", " ")

    await send_edit_photo_callback(callback, media='', send_mode='edit', edit_content='caption', 
                                   caption=f"Выбранное Вами Мероприятие:\n\n{chosen_event_name_date}\n\nБронируемое место: {seat_text}\n\n Все верно?",
                                   is_last_message=is_last_message, 
                                   reply_markup=kb.get_yes_no_kb(seat=seat, event_id=event_id))

    # await bot.edit_message_caption(chat_id=callback.from_user.id,
    #                                message_id=callback.message.message_id, 
    #                                caption=f"Выбранное Вами Мероприятие:\n\n{chosen_event_name_date}\n\nБронируемое место: {seat_text}\n\n Все верно?", 
    #                                 reply_markup=kb.get_yes_no_kb(seat=seat, event_id=event_id))
    await bot.answer_callback_query(callback.id)



@router_club.callback_query(BOOKING_TICKET_CLUB.CHOOSE_TABLE, MyCallback_table_picker.filter(F.valid == True))
async def pre_checkout_validation_club_no_state(callback: CallbackQuery, is_last_message:bool):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)

    await send_edit_message_callback(callback, basic_answer_vars.session_expired, is_last_message=is_last_message)
    await send_edit_message_callback(callback,  basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.session_expired)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await bot.answer_callback_query(callback.id)



@router_club.callback_query(BOOKING_TICKET_CLUB.PRE_CHECKOUT_STATE, MyCallback_table_picker_confirmed.filter(F.confirmed == False))
async def back_to_free_table_set_club(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    callback_data_split = callback.data.split(":") 
    event_id= callback_data_split[3]
    await get_table_set_club(event_id=event_id, paste_mode='edit', callback=callback, state=state, is_last_message=is_last_message)



@router_club.callback_query(BOOKING_TICKET_CLUB.PRE_CHECKOUT_STATE, MyCallback_table_picker_confirmed.filter(F.confirmed == True))
async def confirm_existing_order(callback: CallbackQuery, state: FSMContext, is_last_message:bool):


    awaiting_order_from_user = await database_api.get_awaiting_order_by_user_id(callback.from_user.id)

    if len(awaiting_order_from_user) !=0:
        label_split = awaiting_order_from_user[0][2].split(":")
        event_data = await OneC_api.get_event_data()
        event_id_awaiting = label_split[0]
        event = [event for event in event_data if event['event_id'] == event_id_awaiting][0]
        event_date = await convert_date_representation(event['event_date'])
        chosen_event_name_date = f"{event['event_name']}\n\n{event_date}"
        seat_awaiting = label_split[1]
        seat_replaced_str = seat_awaiting.replace("_", " ")


        await bot.delete_message(callback.from_user.id, callback.message.message_id)

        msg  = await send_edit_message_callback(callback, f'''Для вас ранее уже был создан ордер, ожидающий оплаты:\n\n#order: 
                                                {label_split[0]}:{label_split[2]}\n\n{chosen_event_name_date}\n\nВыбранное место: {seat_replaced_str}''', is_last_message=is_last_message,
                                                 reply_markup=kb.get_existing_order_check_keyboard(event_id_awaiting, awaiting_order_from_user[0][4], seat=seat_awaiting) )
        # msg = await bot.send_message(callback.from_user.id, f'''Для вас ранее уже был создан ордер, ожидающий оплаты:\n\n#order: 
        #                                         {label_split[0]}:{label_split[2]}\n\n{chosen_event_name_date}\n\nВыбранное место: {seat_replaced_str}''', 
        #                         reply_markup=kb.get_existing_order_check_keyboard(event_id_awaiting, awaiting_order_from_user[0][4], seat=seat_awaiting))
        
        message_ids_str = awaiting_order_from_user[0][5]
        message_ids_str = message_ids_str + ";" + str(msg.message_id)

        mod_dict = {}
        mod_dict['message_ids'] = message_ids_str
        
        await database_api.modify_awaiting_order(mod_dict, str(callback.from_user.id))
        await state.set_state(BOOKING_TICKET_CLUB.CHECK_PAY_EXISTS)
        await bot.answer_callback_query(callback.id)
        return
        
    await send_order(callback, state, is_last_message)
    await state.clear()
    await bot.answer_callback_query(callback.id)



@router_club.callback_query(BOOKING_TICKET_CLUB.CHECK_PAY_EXISTS, MyCallback_table_picker_confirmed.filter(F.confirmed == True))
async def send_order_rewrite_exists(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    callback_data_split = callback.data.split(":")

    await database_api.delete_order_by_user_id(callback.from_user.id)
    await OneC_api.set_booking_state(event_id=callback_data_split[0], table=callback_data_split[1], status='Свободно')
    await send_order(callback, state, is_last_message)
    await state.clear()
    await bot.answer_callback_query(callback.id)



@router_club.callback_query(BOOKING_TICKET_CLUB.CHECK_PAY_EXISTS, MyCallback_event_picker_event_picked.filter(F.valid == True))
async def back_to_free_table_set_club_from_order_check(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    callback_data_split = callback.data.split(":") 
    event_id= callback_data_split[2]
    await get_table_set_club(event_id=event_id, paste_mode='send', callback=callback, state=state, is_last_message=is_last_message)



@router_club.callback_query(BOOKING_TICKET_CLUB.CHECK_PAY_EXISTS, MyCallback_table_picker_confirmed.filter(F.confirmed == True))
async def send_order_rewrite(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    await send_order(callback, state, is_last_message)



async def send_order(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    
    """
    создание ордера в платежной системе
    """
    
    if not await is_booking_server_available(callback, is_last_message):
        return
    
    memory_data = await state.get_data()
    try:
        event_data = memory_data['event_data']
    except KeyError:
        event_data = await OneC_api.get_event_data()
    
        


    callback_data_split = callback.data.split(":")
    seat= callback_data_split[2]  
    event_id= callback_data_split[3]
    event = [event for event in event_data if event['event_id'] == event_id][0]

    event_date = await convert_date_representation(event['event_date'])
    chosen_event_name_date = f"{event['event_name']}\n\nДата и время проведения:\n\n{event_date}"


    current_table_configuration = await OneC_api.get_table_configuration_data(event_id)


    current_seat = [elem for elem in current_table_configuration if elem['Место'] == seat]
    chosen_table_price = int(current_seat[0]['Цена'])
    if current_seat[0]['СтатусБронирования'] == "Свободно":
        if await OneC_api.set_booking_state(event_id=event_id, table=seat, status="ОжидаетОплаты") != 200:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
            await send_edit_message_callback(callback, basic_answer_vars.server_unavailable_answer, is_last_message=is_last_message, reply_markup=kb.inline_kb_3)
            #await bot.send_message(callback.from_user.id, basic_answer_vars.server_unavailable_answer, reply_markup=kb.inline_kb_3)
            await bot.answer_callback_query(callback.id)
            return
        
        
        event_payment_ids = await OneC_api.get_event_payment_ids(event_id)
        event_payment_ids = event_payment_ids[event_id]

        selection_orders = await database_api.get_awaiting_orders()
        awaiting_order_ids = [order[2].split(";")[2] for order in selection_orders if  order[2].split(";")[0] == event_id]

        while True:
            unique_payment_id = str(misc.random_with_N_digits(5))
            if unique_payment_id in event_payment_ids and unique_payment_id in awaiting_order_ids:
                continue
            else:
                break

        unique_order_label = event_id + ":" + seat + ":" + unique_payment_id + ":" + str(callback.from_user.id) + ":" + test_payment_mode

        seat_text = seat.replace("_", " ")

        date_order = datetime.now().strftime("%m/%d/%y %H:%M:%S")

        


        quickpay = Quickpay(
            receiver="4100118439131299",
            quickpay_form="button",
            targets=f"Орбита Джаз Клуб\n{chosen_event_name_date}\n{seat}",
            label=unique_order_label,
            paymentType="AC",
            sum=10,
            )
        

        

        await update_awaiting_orders_list() 

        await bot.delete_message(callback.from_user.id, callback.message.message_id)

        msg = await send_edit_message_callback(callback, f'''Сформирован ордер на оплату:\n\n#order {event_id}:{unique_payment_id}\n\nВыбранное Вами Мероприятие:\n\n{chosen_event_name_date}
                                               \nБронируемое место: {seat_text}\n\nСтоимость места: {chosen_table_price} руб.\n\nПеревод осуществляется по ссылке ниже на номер кошелька:\n\n4100118439131299
                                               \nОрдер действителен в течение 20 минут\n\nПосле подтверждения оплаты в течение нескольких минут вы найдете QR-код для доступа на мероприятие в разделе:
                                               \nМои заявки бронирования\n\nБлагодарим Вас за проявленный интерес к дейтельности Клуба!''', is_last_message=is_last_message, 
                                     reply_markup=kb.get_url_button_inline_markup("Оплата банковской картой", URL=quickpay.redirected_url))
    
        # msg = await bot.send_message(callback.from_user.id, f'''Сформирован ордер на оплату:\n\n#order {event_id}:{unique_payment_id}\n\nВыбранное Вами Мероприятие:\n\n{chosen_event_name_date}\n\n
        #                              Бронируемое место: {seat_text}\n\nСтоимость места: {chosen_table_price} руб.\n\nПеревод осуществляется по ссылке ниже на номер кошелька:\n\n4100118439131299\n\n
        #                              Ордер действителен в течение 20 минут\n\nПосле подтверждения оплаты в течение нескольких минут вы найдете QR-код для доступа на мероприятие в разделе:\n\n
        #                              Мои заявки бронирования\n\nБлагодарим Вас за проявленный интерес к дейтельности Клуба!''', 
        #                 reply_markup=kb.get_url_button_inline_markup("Оплата банковской картой", URL=quickpay.redirected_url))
        

        await database_api.add_awaiting_order(user_id=str(callback.from_user.id), order_id=unique_order_label, order_url=quickpay.base_url, date_order=date_order, message_ids=f'{msg.message_id}')
        

        #посмотреть висит ли на пользователе in_process платеж с указанным столом в label, если да предложить ту же ссылку, если нет то создать новую

        # если между awaiting payment размещением и текущим временем больше 20 мину, то удалаем ссылку и отменяем бронирование, сделать связку
        await send_edit_message_callback(callback, "🎷 Орбита Джаз Клуб", is_last_message=is_last_message, reply_markup=kb.inline_kb_3)
        #await bot.send_message(callback.from_user.id, "🎷 Орбита Джаз Клуб", reply_markup=kb.inline_kb_3)
        await bot.answer_callback_query(callback.id)
         
    else:
        current_table_configuration = await OneC_api.get_table_configuration_data(event_id)
        tables_not_booked = [elem for elem in current_table_configuration if "Стол" in elem['Место'] and elem['СтатусБронирования'] == 'Свободно']
        tables_not_booked = natsorted(tables_not_booked, key=lambda x: x['Место'])

        await send_edit_photo_callback(callback, 
                                       media='',
                                       caption=f"К сожалению, данный стол уже забронирован.\n\nПожалуйста, выберите другой стол: \n\nВыбранное Вами Мероприятие:\n\n{chosen_event_name_date}",
                                       reply_markup=kb.gen_table_picker_kb(tables_not_booked, event_id),
                                       send_mode='edit',
                                       edit_content='caption', 
                                       is_last_message=is_last_message)

        # await bot.edit_message_caption(chat_id=callback.from_user.id,
        #                         message_id=callback.message.message_id, 
        #                         caption=f"К сожалению, данный стол уже забронирован.\n\nПожалуйста, выберите другой стол: \n\nВыбранное Вами Мероприятие:\n\n{chosen_event_name_date}",
        #                         reply_markup=kb.gen_table_picker_kb(tables_not_booked, event_id))
        
        await bot.answer_callback_query(callback.id)



@router_club.callback_query(MyCallback_event_picker_event_picked_back.filter(F.valid ==True))
async def back_to_event_review_no_state(callback: CallbackQuery, is_last_message:bool):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass

    await send_edit_message_callback(callback, basic_answer_vars.session_expired, is_last_message)
    await send_edit_message_callback(callback,  basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.session_expired)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await bot.answer_callback_query(callback.id)




@router_club.callback_query(MyCallback_event_picker_event_picked.filter(F.valid == True))
async def get_free_table_set_club_no_state(callback: CallbackQuery, is_last_message:bool):

    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass
    #await bot.send_message(callback.from_user.id, basic_answer_vars.session_expired)
    await send_edit_message_callback(callback, basic_answer_vars.session_expired, is_last_message, reply_markup=None)
    await send_edit_message_callback(callback, basic_answer_vars.default_main_menu_answer, is_last_message, reply_markup=kb.inline_kb_main)
    await bot.answer_callback_query(callback.id)




@router_club.callback_query(MyCallback_table_picker_confirmed.filter(F.confirmed == False))
async def back_to_free_table_set_club_no_state(callback: CallbackQuery, is_last_message:bool):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass

    await send_edit_message_callback(callback, basic_answer_vars.session_expired, is_last_message)
    await send_edit_message_callback(callback, basic_answer_vars.default_main_menu_answer, is_last_message, reply_markup=kb.inline_kb_main)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.session_expired)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await bot.answer_callback_query(callback.id)


@router_club.callback_query(MyCallback_table_picker_confirmed.filter(F.confirmed == True))
async def proceed_to_checkout_club_yes_no_state(callback: CallbackQuery, is_last_message:bool):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass

    await send_edit_message_callback(callback, basic_answer_vars.session_expired, is_last_message)
    await send_edit_message_callback(callback,  basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.session_expired)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await bot.answer_callback_query(callback.id)


@router_club.callback_query(MyCallback_successfull_payment_get_qr_code.filter(F.valid == True))
async def show_qr_code_to_user(callback: CallbackQuery, state: FSMContext, is_last_message:bool):
    if not await is_booking_server_available(callback, is_last_message):
        return
    
    memory_data = await state.get_data()
    user_data = callback.data.split(":")
    event_id = user_data[2]
    order_id = user_data[3]
    QR_str = callback.data.split(":")[4]
    try: 
        payment_data = memory_data['payment_data']
    except KeyError:
        payment_data = await OneC_api.get_book_entry_by_id(callback.from_user.id)

        await state.update_data({'payment_data': payment_data})

    
    operation = [oper for oper in payment_data if oper['event_id'] == event_id and oper['order_id']== order_id][0]

    img = qrcode.make(QR_str)
    buf = io.BytesIO()
    img.save(buf)
    byte_im = buf.getvalue()


    event_name = operation['event_name'] 
    event_date = await convert_date_representation(operation['event_date'])
    seat = operation['table'].replace("_", " ")


    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass


    await send_edit_photo_callback(callback,
                                   media=BufferedInputFile(file = byte_im, filename='invoice_qr_code.png'),
                                   caption=f"Оплаченный ордер:\n\n# order {event_id}:{order_id}\n\n{event_name}\n\n Дата проведения: {event_date}\n\n Забронированное место: {seat}",
                                   send_mode='send',
                                   is_last_message=is_last_message
                                   )
    #await bot.send_photo(callback.from_user.id, BufferedInputFile(file = byte_im, filename='invoice_qr_code.png'), caption=f"Оплаченный ордер:\n\n# order {event_id}:{order_id}\n\n{event_name}\n\n Дата проведения: {event_date}\n\n Забронированное место: {seat}")

    await send_edit_message_callback(callback, f'''Оплаченный ордер:\n\n# order {event_id}:{order_id}\n\n{event_name}\n\n Дата и время проведения:\n\n
                                     {event_date}\n\n Забронированное место:{seat}''', is_last_message=is_last_message, reply_markup=kb.get_success_payments_kb(QR_str, event_id, order_id))
    #await bot.send_message(callback.from_user.id, f"Оплаченный ордер:\n\n# order {event_id}:{order_id}\n\n{event_name}\n\n Дата и время проведения:\n\n{event_date}\n\n Забронированное место:{seat}", reply_markup=kb.get_success_payments_kb(QR_str, event_id, order_id))
    await bot.answer_callback_query(callback.id)

 
@router_club.callback_query(MyCallback_successfull_payment_get_qr_code.filter(F.valid == True))
async def show_qr_code_to_user_no_state(callback: CallbackQuery, is_last_message:bool):
    try:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    except TelegramBadRequest:
        pass

    await send_edit_message_callback(callback, basic_answer_vars.session_expired, is_last_message)
    await send_edit_message_callback(callback,  basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)

    # await bot.send_message(callback.from_user.id, basic_answer_vars.session_expired)
    # await bot.send_message(callback.from_user.id, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await bot.answer_callback_query(callback.id)

 
async def is_booking_server_available(callback, is_last_message:bool):

    if not await OneC_api.is_server_available():
        
        try:
            await bot.delete_message(callback.from_user.id, callback.message.message_id)
        except TelegramBadRequest:
            pass

        await send_edit_message_callback(callback, basic_answer_vars.server_unavailable_answer, reply_markup=kb.inline_kb_3, is_last_message=is_last_message)
        #wait bot.send_message(callback.from_user.id, basic_answer_vars.server_unavailable_answer, reply_markup=kb.inline_kb_3)
        await bot.answer_callback_query(callback.id)
        return False
    else: 
        return True
    