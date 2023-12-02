from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from app.database.redis_storage import redis_client



class Last_Message_Middleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        
        
        user_id = data['event_from_user'].id
        if event.event_type == 'message':
            msg_id = event.message.message_id
        elif event.event_type == 'callback_query':
            msg_id = event.event.message.message_id

        redis_key = 'last_message' + ":" + str(user_id)
        last_msg_id = redis_client.get(redis_key)
        if last_msg_id == None:
            data['is_last_message'] = True
        else:
            if int(last_msg_id) == int(msg_id):
                data['is_last_message'] = True
            else:
                data['is_last_message'] = False


        result = await handler(event, data)
        return result
    

class My_MiddleWare(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        user_id = data['event_from_user'].id
        if  user_id != 1019910117:
            return
        else:
            result = await handler(event, data)
            return result