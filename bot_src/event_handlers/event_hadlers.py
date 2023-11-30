from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from keyboards import keyboards as kb
from aiogram.filters import Command
from standard_answers import basic_answer_vars
from state_context.state_context import REQUEST_CONTACT
from API import database_api
from aiogram.types import ContentType
from aiogram.enums.chat_member_status import ChatMemberStatus
from bot_init import bot
from database.redis_storage import redis_client



router = Router()

# EVENT HANDLERS
@router.message(Command('start'))
async def process_start_command(message: types.Message, state:FSMContext, is_last_message: bool):
    
    if await database_api.contact_in_db(user_id = message.from_user.id):
        msg = await message.answer(basic_answer_vars.start_command_text, reply_markup=kb.reply_main_markup)
        await bot.delete_message(message.from_user.id, msg.message_id)
        await message.answer(basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    else:
        await message.answer(basic_answer_vars.phone_request_answer_initial,reply_markup=kb.request_phone_kb())
        await state.set_state(REQUEST_CONTACT.REQUEST_CONTACT)



@router.message(Command('menu'))
async def process_start_command(message: types.Message, state:FSMContext, is_last_message: bool):
    await state.clear()
    await message.answer(basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
        


@router.message(F.text == '🏡Главное меню')
async def reply_to_main(message: types.Message):
    await message.answer(basic_answer_vars.default_main_menu_answer,reply_markup=kb.inline_kb_main)
    

@router.message(Command('send_contacts'))
async def process_start_command(message: types.Message):
    await message.answer(basic_answer_vars.phone_request_answer_repeat,reply_markup=kb.request_phone_kb())
    


@router.message(F.content_type.in_({ContentType.CONTACT}))
async def request_contact_yes(message:types.Message, state: FSMContext, is_last_message: bool):
    await database_api.add_user_to_db(str(message.from_user.id), message.contact.phone_number, message.contact.first_name, message.contact.last_name)
    await message.answer("Контакты записали. Спасибо!", reply_markup=kb.reply_main_markup)
    await bot.send_message(message.from_user.id, basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await state.clear()


@router.message(REQUEST_CONTACT.REQUEST_CONTACT)
async def request_contact_no(message:types.Message, state: FSMContext, is_last_message: bool):
    await database_api.add_user_to_db(str(message.from_user.id),'', message.from_user.first_name,  message.from_user.last_name)
    await message.answer(basic_answer_vars.default_main_menu_answer, reply_markup=kb.inline_kb_main)
    await state.clear()



@router.message(Command('admin'))
async def process_start_command(message: types.Message, is_last_message: bool):
    member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if member.status == ChatMemberStatus.MEMBER:
        await bot.send_message(message.from_user.id, "Панель администратора", reply_markup=kb.inline_kb_admin)   

@router.message()
async def unhandled_messages(message: types.Message, is_last_message: bool):
    redis_key = 'last_message' + ":" + str(message.from_user.id)
    redis_client.set(redis_key, message.message_id)