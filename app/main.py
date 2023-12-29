import os

os.environ['BOT_TOKEN'] = "6861178653:AAERKAeAEKQunpXfi5no85ZYrKKbxMHOUcw"
os.environ['YM_TOKEN'] = "4100118439131299.DEA1C33FB092FEC77ECE535E62319496D6C667DD1C6A325E12B2E5B7B4020888D8F2338F603C19DD6C29428C83AE74707A04A389984215F559C542BD4EEF0C588031C7D2774DC528DC79EB2A8D1E72F476C3AB20C3F3A79DA94D2795E675B4A509AF9B46F73EE417C828F4E8FD5414927FE459BE21B179827BABDCA0A5288B01"
os.environ['VK_LOGIN'] = "+79150598207"
os.environ['VK_PASSWORD'] = "UeXj5f#D5YrL5*gQ"
os.environ['VK_ACCESS_TOKEN'] = "vk1.a.dLI7gUdclGWcG051o5Vwo96wZe906cdSS0AUO4F6Tl4WWDSfb2RfkZrJNRz4OUiRtry2A8-2JnC6umn7rAr1fxB6geiYlgZOR3eXm4ATZkOUZtEtoKVGnB8o-wdv6-RTeeLvgHL9PMgkBF1Gw-a8psjkPSkFksl6VTsMfpMXKfigweO4EG-LuBKvJQ52D5jCVFuDDLYbkcmqi-2RG1l3Vg"
os.environ['SQLITE3_PATH'] = r"C:\Users\tarousinsk1997\Documents\hotel_orbita_bot\database\tgbot_database.db"     

os.environ['REDIS_URL'] = "redis://localhost:6873/0"
os.environ['INFO_BASE_NAME'] = "InfoBase"
os.environ['INFO_BASE_HOST'] = "localhost:80"


PYTHONUNBUFFERED=1



import asyncio
import logging

import ssl
import time
import sys
from aiohttp import web
from datetime import datetime
from aiogram import Dispatcher, Bot
from aiogram.types import FSInputFile
from bot_src.bot_init import bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot_src.middlewares.middleware import Last_Message_Middleware, My_MiddleWare
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import nest_asyncio
from database.redis_storage import redis_storage
from bot_src.scheduled_tasks import compare_payment_history, vk_api_query, update_awaiting_orders_list
from bot_src.API.web_server_api import routes


nest_asyncio.apply()


from bot_src.event_handlers import event_hadlers
from bot_src.callback_handlers import callback_club, callback_default, callback_qr

fn = datetime.now().strftime('logs/test.py-%Y%m%d%H%M%S.log')


dp = Dispatcher(storage=redis_storage)


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(compare_payment_history, trigger='interval', seconds=10)
    scheduler.add_job(update_awaiting_orders_list, trigger='interval', seconds=60)
    scheduler.start()

    # WEBHOOK
    #await bot.set_webhook(WEBHOOK_URL, certificate=FSInputFile(WEBHOOK_SSL_CERT))




dp.include_routers(event_hadlers.router, callback_default.router_deafult, callback_club.router_club)
dp.startup.register(on_startup)


dp.update.outer_middleware(My_MiddleWare())
dp.update.middleware(Last_Message_Middleware())




cdir = os.getcwd()





async def print_hello():
    print('WORKS')


async def main():

    
    #await vk_api_query()
    await compare_payment_history()
    await update_awaiting_orders_list()


# WEBHOOK

    # app = web.Application()
    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot)
    # webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    # setup_application(app, dp, bot=bot)
    # app.add_routes(routes)

    #     # Generate SSL context
    # context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)


    #web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT, ssl_context=context)


    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.getLogger('requests').setLevel(logging.INFO)

    logging.basicConfig(
        #filename=os.getcwd() + '/app/database/bot_log.log',
         stream=sys.stdout,
          level=logging.DEBUG)

    asyncio.run(main())
    