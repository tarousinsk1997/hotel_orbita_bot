import asyncio
import logging
import os
import time
from aiohttp import web
from datetime import datetime
from aiogram import Dispatcher, Bot
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
    #await bot.set_webhook(WEBHOOK_URL)




dp.include_routers(event_hadlers.router, callback_default.router_deafult, callback_club.router_club)
dp.startup.register(on_startup)


dp.update.outer_middleware(My_MiddleWare())
dp.update.middleware(Last_Message_Middleware())



# Webserver settings
# bind localhost only to prevent any external access
WEB_SERVER_HOST = "127.0.0.1"
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = 8443

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/webhook"
# Secret key to validate requests from Telegram (optional)
#WEBHOOK_SECRET = "my-secret"
# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public address with TLS support
BASE_WEBHOOK_URL = "https://arguably-concise-stinkbug.ngrok-free.app"

WEBHOOK_URL = f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}"

# Path to SSL certificate and private key for self-signed certificate.
# WEBHOOK_SSL_CERT = "/path/to/cert.pem"
# WEBHOOK_SSL_PRIV = "/path/to/private.key"






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
    #web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.getLogger('requests').setLevel(logging.WARNING)

    logging.basicConfig(filename=os.getcwd() + '/app/database/bot_log.log', level=logging.ERROR)

    logging.basicConfig(filename='/database/bot_log.log', level=logging.ERROR)

    asyncio.run(main())
    