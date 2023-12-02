# from aiogram import F, types, Router
# from aiogram.types import ContentType
# import requests
# import numpy as np
# from bot_src.credentials.credentials import creds

# from PIL import Image
# import cv2

# from qreader import QReader

# from bot_src.state_context.state_context import QR_VALIDATION


# QREADER = QReader(model_size = 'n', min_confidence = 0.5)

# router_qr = Router()
# from bot_src.bot_init import bot

# @router_qr.message(QR_VALIDATION.CHOOSE_EVENT, F.content_type.in_([ContentType.PHOTO]))
# async def qr_validation(message: types.Message):


#     qr_photo = await bot.get_file(message.photo[-1].file_id)
#     file_path = qr_photo.file_path
#     url_download = f"https://api.telegram.org/file/bot{creds['api_token_bot']}/{file_path}"
#     img = Image.open(requests.get(url_download, stream=True).raw)
#     image = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
#     decoded_text = QREADER.detect_and_decode(image=image)
#     await message.answer(decoded_text[0])
#     await message.answer('Сфоротографируйте QR-код для валдиации')