from bot_src.credentials.credentials import creds
from aiogram import Bot
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot()


