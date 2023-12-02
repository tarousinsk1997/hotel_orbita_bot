from aiogram.fsm.storage.redis import RedisStorage
from redis import Redis
import os


REDIS_URL = 'redis://localhost:6379/0'
#REDIS_URL = os.getenv('REDIS_URL')

redis_storage = RedisStorage.from_url(REDIS_URL, state_ttl=3600, data_ttl=30)
redis_client = Redis()

for key in redis_client.scan_iter('last_message:*'):
    redis_client.delete(key)




