from yoomoney import Client
import json
import re
import os


YM_TOKEN = os.getenv('YM_TOKEN')
client = Client(YM_TOKEN)

def get_operation_history_json(operation_history):
    for operation in operation_history:
        operations_dict = {}
        if operation.label != None:
            operations_dict[operation.operation_id] = {'status': operation.status,
                                            'datetime' : operation.datetime.strftime("%Y%m%d%H%m%S"),
                                            'title': operation.title,
                                            'pattern_id': operation.pattern_id,
                                            'direction': operation.direction,
                                            'amount': operation.amount,
                                            'label': operation.label,
                                            'type': operation.type

            }

        return json.loads(json.dumps(operations_dict))

# pattern = re.compile(".{1,}:.{1,}:.{1,}:.{1,}")
# history_operations = client.operation_history(type="deposition", records=100).operations
# history_operations = get_operation_history_json(history_operations)
# history_operations_target = {k: v  for k, v in history_operations.items() if bool(re.match(pattern, v['label'])) and v['status'] =='success'}

# print(history_operations)

#  
# # print("List of operations:")
# # print("Next page starts with: ", history.next_record)

# # for operation in history.operations:
# #     print()
# #     print("Operation:",operation.operation_id)
# #     print("\tStatus     -->", operation.status)
# #     print("\tTitle      -->", operation.title)
# #     print("\tAmount     -->", operation.amount)
# #     print("\tLabel      -->", operation.label)

# details = client.operation_details(operation_id="753223135421578120")

# # payment_form =
# # {
# #   "title": "Форма оплаты бронирования Орбита Джаз Клуб",
# #   "form": [
# #     {
# #       "type": "text",
# #       "name": "supplier_name",
# #       "label": "Фамилия и Имя",
# #       "hint": "Пожалуйста, введите Вашу Фамилию и Имя"
# #       "alert": "Данные указаны некорретно",
# #       "required": "true",
# #       "readonly": "false",
# #       "minlength": 1,
# #       "maxlength": 30,
# #       "pattern": r"[А-Яа-яA-Za-z]{1,}\s[А-Яа-яA-Za-z]{1,}\s?[А-Яа-яA-Za-z]{1,}?"
# #     },

# #     {
# #       "type": "text",
# #       "name": "supplier_phone",
# #       "label": "Номер телефона для связи (необязательно)",
# #       "hint": "Пожалуйста, введите Ваш номер телефона"
# #       "alert": "Данные указаны некорретно",
# #       "required": "false",
# #       "readonly": "false",
# #       "minlength": 1,
# #       "maxlength": 30,
# #       "pattern": r"\+?\d{10,11}"
# #     },

# #     {
# #       "type": "submit",
# #       "label": "Продолжить"
# #     }
# #   ],
# #   "money_source": [
# #     "wallet",
# #     "cards",
# #     "payment-card",
# #   ],
# # }




