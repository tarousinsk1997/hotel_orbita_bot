from aiogram.types import CallbackQuery, InputMediaPhoto, BufferedInputFile, ReplyKeyboardMarkup, InlineKeyboardMarkup, ReplyKeyboardRemove, Message

from app.bot_src.bot_init import bot
from app.database.redis_storage import redis_client



async def send_edit_message_callback(callback: CallbackQuery, text:str, reply_markup:object, is_last_message:bool=True, send_mode: str='send'):
    if not is_last_message:
        msg = await bot.send_message(callback.from_user.id, text, reply_markup=reply_markup)
    else:
        if send_mode == 'send':
            msg = await bot.send_message(callback.from_user.id, text, reply_markup=reply_markup)
        elif send_mode == 'edit':
            msg = await bot.edit_message_text(text, callback.from_user.id, callback.message.message_id, reply_markup=reply_markup)
        else:
            raise  ValueError("Wrong Send mode provided")
    
    redis_key = 'last_message' + ":" + str(callback.from_user.id)
    redis_client.set(redis_key, msg.message_id)
    
    return msg
        


async def send_edit_photo_callback(callback: CallbackQuery, media: str | InputMediaPhoto | BufferedInputFile,  caption:str, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | None = None, send_mode: str='send', edit_content:str='caption', is_last_message:bool=True, ):
    imf = InputMediaPhoto(media=media)
    if not is_last_message:
        msg = await bot.send_photo(callback.from_user.id, photo=media, caption=caption, reply_markup=reply_markup)
    else:
        if send_mode == 'send':
            msg = await bot.send_photo(callback.from_user.id, photo=media, caption=caption, reply_markup=reply_markup)
        elif send_mode == 'edit':
            if edit_content == 'caption':
                msg = await bot.edit_message_caption(callback.from_user.id, callback.message.message_id, caption=caption, reply_markup=reply_markup)
            elif edit_content == 'media':
                msg = await bot.edit_message_media(imf, callback.from_user.id, callback.message.message_id, reply_markup=reply_markup)
            else:
                raise ValueError("Wrong content type provided")
        else:
            raise  ValueError("Wrong Send mode provided")
        
    redis_key = 'last_message' + ":" + str(callback.from_user.id)
    redis_client.set(redis_key, msg.message_id, ex=3600)

    return msg




