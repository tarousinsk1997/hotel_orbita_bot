import vk_api
from bot_src.credentials.credentials import creds
from bot_src.API.vkapi import auth_handler_vk, captcha_handler_vk
from database.redis_storage import redis_client
from bot_src.API import yoomoney_api
from bot_src.bot_init import bot
from bot_src.API import OneC_api
import uuid
from bot_src.API import database_api
import re
import json
import os
from datetime import datetime
from bot_src.keyboards import keyboards as kb



test_payment_mode = '1'

# .isoformat(sep='T', timespec='milliseconds')


async def vk_api_query():

    VK_LOGIN = os.getenv('VK_LOGIN')
    VK_PASSWORD = os.getenv('VK_PASSWORD')
    global gl_last_post
    gl_last_post = {}

    vk_api_session = vk_api.VkApi(login =VK_LOGIN, 
                                password=VK_PASSWORD, 
                                auth_handler=auth_handler_vk,
                                captcha_handler=captcha_handler_vk, 
                                app_id=2685278)

    
    
    vk_api_session.auth(token_only=True)
    vkapi_API = vk_api_session.get_api()

    post_content = vkapi_API.wall.get(owner_id=creds["owner_id"],
                        count=2,
                        filter='all',
                        )
  
    gl_last_post['text'] = post_content["items"][0]["text"]
    attachments = post_content['items'][0]['attachments']
    photos_list = []
    for attachament in attachments:
        if attachament['type'] == 'photo':
            photos_list.append(f"{attachament['photo']['owner_id']}_{attachament['photo']['id']}")
    
    photos_string = ','.join(photos_list)
    
    photo_array = vkapi_API.photos.getById(photos=photos_string)
    

    
    gl_last_post['photos'] = photo_array
    gl_last_post['content'] = post_content


regexp_pattern_payment_label = re.compile(".{1,}:.{1,}:.{1,}:.{1,}:" + test_payment_mode)
async def compare_payment_history() -> None:

    if not await OneC_api.is_server_available():
        return
    # 1 get history in yoomoney
    event_data = await OneC_api.get_event_data()
    for event in event_data:
        from_date = datetime.strptime(event['event_date_creation'], OneC_api.format_date_str).astimezone()
        till_date = datetime.now().astimezone()
        history_operations_wallet = yoomoney_api.client.operation_history(type="deposition", records=100, from_date=from_date, till_date=till_date).operations
        history_json_wallet = yoomoney_api.get_operation_history_json(history_operations_wallet)
        history_operations_target = {k: v  for k, v in history_json_wallet.items() if bool(re.match(regexp_pattern_payment_label, v['label'])) and v['status'] =='success'}
        # 2 get payment identifiers from 1c
        payment_records_1c = await OneC_api.get_event_payment_ids("all")


        for operation in history_operations_target:
            operation_label_properties = history_operations_target[operation]['label'].split(":")
            event_id = operation_label_properties[0]
            unique_payment_id = operation_label_properties[2]
            #await database_api.delete_order_by_label_id(history_operations_target[operation]['label'])
            
            #unique_order_label = chosen_event_id + ":" + chosen_table + ":" + unique_payment_id + ":" + str(message.from_user.id)
            if unique_payment_id not in payment_records_1c[event_id]:
                #Добавление записи в базу 1с об успешной оплате
                table = operation_label_properties[1]
                user_id = operation_label_properties[3]
                chat = await bot.get_chat(user_id)
                fullname = chat.full_name
                nickname_telegram = chat.username
                booking_date_time = history_operations_target[operation]['datetime']
                amount = history_operations_target[operation]['amount']
                unique_qr_data = str(uuid.uuid4())
                order_id = event_id + ":" + unique_payment_id

                phone_number = await database_api.get_phone_number(user_id)

                #отправка записи в 1с

                resonse = await OneC_api.post_book_entry(event_id=event_id,
                                        unique_payment_id=unique_payment_id,
                                        user_id=user_id,
                                        table_id=table,
                                        full_name=fullname,
                                        nickname=nickname_telegram,
                                        booking_date_time=booking_date_time,
                                        amount=amount,
                                        unique_qr_data=unique_qr_data,
                                        phone_number=phone_number
                )
                
                await OneC_api.set_booking_state(event_id, table, "Оплачено")
                await database_api.delete_order_by_user_id(user_id)
                await bot.send_message(int(user_id), f"#order {order_id} оплачен!\n\nВы найдёте QR-код для доступа не мероприятия в разделе активных оплаченных заявок по кнопке ниже:")
                await bot.send_message(int(user_id), f"Мои заявки бронирования", reply_markup=kb.inline_kb_3_4)
                print(resonse.status_code)



async def update_awaiting_orders_list():
    await database_api.delete_expiring_orders_from_db()
    selection = await database_api.get_awaiting_orders()
    selection_json = json.dumps(selection)
    redis_client.set('awaiting_orders', selection_json)

