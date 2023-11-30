import sqlite3
from datetime import datetime, timedelta
from bot_src.API import OneC_api
from aiogram.exceptions import TelegramBadRequest
from bot_src.bot_init import bot

SQLITE3_PATH = 'D:\Python Projects\hotel_orbita_bot\database\my_database.db'
db_connection = sqlite3.connect(SQLITE3_PATH)
# cursor = connection.cursor()

# cursor.execute('''
# ALTER TABLE Temp_Booking
#                ADD order_url TEXT not NULL
# ''')


# cursor.execute('''
# DROP TABLE Temp_Booking
#                ''')

#cursor.execute('CREATE INDEX idx_order_id ON Temp_Booking (order_id)')
#cursor.execute('CREATE INDEX idx_telegram_id ON Temp_Booking (telegram_id)')
#cursor.execute('CREATE INDEX idx_order_url ON Temp_Booking (order_url)')

# connection.commit()
# connection.close()



#(telegram_id, phone_number) VALUES (?, ?, ?)', (user_id, phone_number)

#Temp_Booking (telegram_id, order_id, date, order_url) VALUES (?, ?, ?, ?)'



#формат даты 1c
# datetime_str = '09/19/22 13:55:26'

# datetime_object = datetime.strptime(datetime_str, '%m/%d/%y %H:%M:%S')


async def add_user_to_db(user_id, phone_number, first_name, last_name):

    cursor = db_connection.cursor()
    sel = cursor.execute('SELECT phone_number FROM Users WHERE telegram_id = ?', (user_id,)).fetchall()
    if len(sel) == 0:
        cursor.execute('INSERT INTO Users (telegram_id, phone_number, first_name, last_name, contacts_requested) VALUES (?, ?, ?, ?, ?)', (user_id, phone_number, first_name, last_name , 1))
    else:
        cursor.execute('UPDATE Users SET phone_number = ?, first_name = ?, last_name = ?, contacts_requested = ? WHERE telegram_id = ?', ( phone_number, first_name, last_name, 1, user_id,))

    db_connection.commit()



async def add_awaiting_order(user_id, order_id, date_order, order_url, message_ids):

    cursor = db_connection.cursor()

    #проверяем, что нет добавляемой строки в базе
    
    cursor.execute('INSERT INTO Temp_Booking (telegram_id, order_id, order_date, order_url, message_ids) VALUES (?, ?, ?, ?, ?)', (user_id, order_id, date_order, order_url, message_ids))
    db_connection.commit()


async def delete_expiring_orders_from_db():

    if not await OneC_api.is_server_available():
        return

    datetime_now = datetime.now()
    cursor = db_connection.cursor()
    
    selection = cursor.execute(f'SELECT * FROM Temp_Booking').fetchall()

    if len(selection) !=0:
        for elem in selection:

            if datetime_now - datetime.strptime(elem[3], '%m/%d/%y %H:%M:%S') > timedelta(seconds=60, 
                                                                                          #minutes=60
                                                                                          ):
                
                user_id = elem[1]
                messages_to_delete = elem[5].split(";")

                for message in messages_to_delete:
                    try:
                        await bot.delete_message(int(user_id), message_id=int(message))
                    except TelegramBadRequest:
                        pass

                label_splitted = elem[2].split(":")
                event_id = label_splitted[0]
                seat = label_splitted[1]
                cursor.execute(f'DELETE FROM Temp_Booking WHERE telegram_id = ?', (user_id,))
                await OneC_api.set_booking_state(event_id=event_id, table=seat, status='Свободно')
                db_connection.commit()


    


async def delete_order_by_user_id(user_id):
    cursor = db_connection.cursor()
    selection = await get_awaiting_order_by_user_id(user_id)

    try:
        messages_to_delete = selection[0][5].split(";")
    except IndexError:
        messages_to_delete = []

    for message in messages_to_delete:
        try:
            await bot.delete_message(int(user_id), message_id=int(message))
        except TelegramBadRequest:
            pass

    cursor.execute(f'DELETE FROM Temp_Booking WHERE telegram_id = ?', (user_id,))
    db_connection.commit()


async def delete_order_by_label_id(label):
    cursor = db_connection.cursor()
    cursor.execute(f'DELETE FROM Temp_Booking WHERE order_id = ?', (label,))
    db_connection.commit()




async def get_awaiting_orders():
    cursor = db_connection.cursor()
    selection = cursor.execute(f'SELECT * FROM Temp_Booking').fetchall()
    return selection


async def get_awaiting_order_by_user_id(user_id):
    cursor = db_connection.cursor()
    selection = cursor.execute(f'SELECT * FROM Temp_Booking WHERE telegram_id = ?', (user_id,)).fetchall()
    return selection


async def modify_awaiting_order(update_dict: dict, user_id):
    cursor = db_connection.cursor()
    param_list = []

    sql_query = 'UPDATE Temp_Booking SET '

    for k,v in update_dict.items():
        sql_query += f'{k} = ? , '
        param_list.append(v)

    param_list.append(str(user_id))
    params = tuple(param_list)
    sql_query = sql_query[:len(sql_query) - 2]
    sql_query += ' WHERE telegram_id = ?'
    cursor.execute(sql_query, params)
    db_connection.commit()






async def contact_in_db(user_id):

    cursor = db_connection.cursor()


    selection = cursor.execute(f'SELECT * FROM Users WHERE telegram_id = {user_id} AND contacts_requested = 1').fetchall()

    if len(selection) == 0:
        return False
    else:
        return True


async def get_phone_number(user_id):
    cursor = db_connection.cursor()
    selection = cursor.execute(f'SELECT phone_number FROM Users WHERE telegram_id = {user_id}').fetchall()

    if len(selection) ==0:
        return 'Номер телефона не предоставлен'
    else:
        return selection[0][0]


