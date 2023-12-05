import requests
import os
import ssl




#s = requests.Session()


format_date_str = '%Y-%m-%dT%H:%M:%S'


info_base_name = os.getenv("INFO_BASE_NAME")
info_base_host = os.getenv("INFO_BASE_HOST")

async def get_event_data():
    """
    returns JSON File from 1c

    event = event_data[0]
    event['event_URL']
    event['event_date']
    event['event_id']
    event['event_name']
    event['event_URL']
    event['event_description']

    """
    response = requests.get(f"{info_base_host}/{info_base_name}/hs/api_telegram_bot/get_events")
    if response.status_code != 200:
        return response.status_code
    
    else: 
        return response.json()
    
async def get_table_configuration_data(event_id):
    """
    returns JSON File of Table configuration from 1c
    """
    
    response = requests.get(f"{info_base_host}/{info_base_name}/hs/api_telegram_bot/get_conf/{event_id}")
    if response.status_code != 200:
        return response.status_code

    else: 
        return response.json()


async def set_booking_state(event_id, table, status):
    response = requests.get(f"{info_base_host}/{info_base_name}/hs/api_telegram_bot/set_booking_status/{status}/{event_id}/{table}")
    return response.status_code


async def get_event_payment_ids(event_id):

    response = requests.get(f"{info_base_host}/{info_base_name}/hs/api_telegram_bot/get_book_ids/{event_id}")
    if response.status_code != 200:
        return response.status_code

    else: 
        return response.json()
    

async def post_book_entry(event_id,
                     unique_payment_id,
                     table_id,
                     user_id,
                     full_name,
                     nickname,
                     booking_date_time,
                     amount,
                     unique_qr_data,
                     phone_number
                     ):
    response = requests.get(f"{info_base_host}/{info_base_name}/hs/api_telegram_bot//post_book_entry/{event_id}/{unique_payment_id}/{table_id}/{user_id}/{full_name}/{nickname}/{booking_date_time}/{amount}/{unique_qr_data}/{phone_number}")
    return response
    

# response = post_book_entry('000000002','64563','Стол_6', '1019910117', 'Никита Андреев', 'Nikita_Andreev_v', '20231116161141', 9.7, '68513fdd-1242-4b84-94fc-f0f8b8281408')
# tables = get_table_configuration_data("000000002")
# print(response)


async def get_book_entry_by_id(telegram_user_id):
    response = requests.get(f"{info_base_host}/{info_base_name}/hs/api_telegram_bot/get_successful_entries/{telegram_user_id}")
    if response.status_code != 200:
        return response.status_code

    else: 
        return response.json()
    

async def is_server_available():
    response = requests.get(f"{info_base_host}/{info_base_name}/hs/api_telegram_bot/server_available")
    if response.status_code != 200:
        return False

    else: 
        return True
    

async def set_turnout_state(event_id: str, seat: str, state:bool):
    
    response = requests.get(f"{info_base_host}/{info_base_name}/hs/api_telegram_bot//set_turnout_state/{event_id}/{seat}/{state}")
    if response.status_code != 200:
        return False
    else: 
        return True



# 1019910117
# responce = get_table_configuration_data("000000002")
# event_data = get_event_data()
# print(event_data[0])



