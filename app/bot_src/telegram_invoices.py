

# @router.message(Command('buy'))
# async def buy(message: types.Message):
#     if creds['payment_token'].split(':')[1] == 'TEST':
#         await bot.send_message(message.chat.id, "Тестовый платеж!!!")
#     await bot.send_invoice(message.chat.id,
#                            title="Подписка на бота",
#                            description="Активация подписки на бота на 1 месяц",
#                            provider_token=creds['payment_token'],
#                            currency="rub",
#                            photo_url="https://selectel.ru/blog/wp-content/uploads/2022/09/Screenshot-2022-09-16-at-11.43.55.png",
#                            photo_width=416,
#                            photo_height=234,
#                            photo_size=416,
#                            is_flexible=False,
#                            prices=[PRICE],
#                            start_parameter="one-month-subscription",
#                            payload = 'test_invoice_payload')


# pre checkout  (must be answered in 10 seconds)
# @router.pre_checkout_query()
# async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
#     await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# @router.message(USER_STATE.DEFAULT_STATE)
# async def get_photo_ids(message: types.Message):
#     print(message.photo[-1].file_id)


# successful payment
# @router.message(F.content_type.in_([ContentType_aiogram.SUCCESSFUL_PAYMENT]))
# async def successful_payment(message: types.Message):
#     print("SUCCESSFUL PAYMENT:")

#     payment_info = iter(message.successful_payment)
#     payment_info_message = ""
#     provider_id_charge = message.successful_payment.provider_payment_charge_id
#     for elem in payment_info:
#         payment_info_message += f"{elem[0]} - {elem[1]}\n"


#     await bot.send_message(message.chat.id,
#                            payment_info_message)
#     img = qrcode.make(provider_id_charge)
#     buf = io.BytesIO()
#     img.save(buf, format='JPEG')
#     byte_im = buf.getvalue()

#     buffer_image = BufferedInputFile(file = byte_im, filename='invoice_qr_code.png')

#     await bot.send_photo(message.chat.id,
#                            buffer_image)