from aiogram import F, Router
from aiogram.types.callback_query import CallbackQuery
from app.bot_src.keyboards import keyboards as kb

from app.bot_src.callback_handlers.callback_classes import MyCallback_rest, MyCallback_rest_back


from app.bot_src.event_handlers.base_answer_function import send_edit_message_callback
from app.bot_src.standard_answers import basic_answer_vars

from app.bot_src.bot_init import bot

router_deafult = Router()


@router_deafult.callback_query(MyCallback_rest_back.filter(F.button_descriptor =='to_main_kb'))
async def back_to_main_kb(callback: CallbackQuery, is_last_message:bool): 
    #await bot.delete_message(callback.from_user.id, callback.message.from_user.id)       
    await send_edit_message_callback(callback,
                                     text=basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main,
                                      send_mode='edit', is_last_message=is_last_message)
    #await bot.edit_message_text('Главное меню Бота', callback.from_user.id, callback.message.message_id, reply_markup=kb.inline_kb_main) 
    await bot.answer_callback_query(callback.id)


# @router.callback_query(MyCallback_jazz_club_back.filter(F.button_descriptor =='to_main_kb'))
# async def to_main_kb(callback: CallbackQuery, state: FSMContext): 
#     #await bot.delete_message(callback.from_user.id, callback.message.from_user.id)       
#     await bot.answer_callback_query(callback.id)
#     await bot.edit_message_text('Главное меню Бота', callback.from_user.id, callback.message.message_id, reply_markup=kb.inline_kb_main) 


@router_deafult.callback_query(MyCallback_rest.filter(F.button_descriptor == "to_rest_main_kb"))
async def to_main_rest_page(callback: CallbackQuery, is_last_message:bool):        
    await send_edit_message_callback(callback,
                                    text=basic_answer_vars.default_rest_menu_answer, reply_markup=kb.inline_kb_2,
                                    send_mode='edit', is_last_message=is_last_message)
    await bot.answer_callback_query(callback.id)
    #await bot.edit_message_text('Главное меню ресторана', callback.from_user.id, callback.message.message_id, reply_markup=kb.inline_kb_2)
       


@router_deafult.callback_query(MyCallback_rest_back.filter(F.button_descriptor == "to_rest_main_kb"))
async def back_to_main_rest_page(callback: CallbackQuery, is_last_message:bool):  

    await send_edit_message_callback(callback,
                                text=basic_answer_vars.default_rest_menu_answer, reply_markup=kb.inline_kb_2,
                                send_mode='edit', is_last_message=is_last_message)      
    await bot.edit_message_text(basic_answer_vars.default_rest_menu_answer, callback.from_user.id, callback.message.message_id, reply_markup=kb.inline_kb_2) 
    await bot.answer_callback_query(callback.id) 

@router_deafult.callback_query(MyCallback_rest.filter(F.button_descriptor == "show_rest_links"))
async def to_restaurant_links(callback: CallbackQuery, is_last_message:bool):        
 
    await send_edit_message_callback(callback,
                            text='Раздел Меню ресторана Орбита', 
                            reply_markup=kb.inline_kb_2_3,
                            send_mode='edit', is_last_message=is_last_message)  
    await bot.answer_callback_query(callback.id) 
    
    #await bot.edit_message_text('Здесь вы найдете ссылки на меню ресторана Орбита', callback.from_user.id, callback.message.message_id, reply_markup=kb.inline_kb_2_3) 
     




