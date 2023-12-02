from aiogram import Bot
import os

TOKEN = os.environ['BOT_TOKEN']

print(TOKEN, flush=True)
bot = Bot(TOKEN)


