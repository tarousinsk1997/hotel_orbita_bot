def auth_handler_vk():
    key = input('2FA: ')
    remember_device = True
    return key, remember_device

def captcha_handler_vk(captcha):
    """ При возникновении капчи вызывается эта функция и ей передается объект
        капчи. Через метод get_url можно получить ссылку на изображение.
        Через метод try_again можно попытаться отправить запрос с кодом капчи
    """

    key = input(f"Enter captcha code : {captcha.get_url()}".strip())

    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)
    


