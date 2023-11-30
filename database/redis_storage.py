from aiogram.fsm.storage.redis import RedisStorage
from redis import Redis

redis_storage = RedisStorage.from_url('redis://localhost:6379/0', state_ttl=3600, data_ttl=30)
redis_client = Redis()

for key in redis_client.scan_iter('last_message:*'):
    redis_client.delete(key)





