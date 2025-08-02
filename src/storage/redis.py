from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from src.core import settings


def get_redis_storage():
    redis = Redis.from_url(settings.REDIS_URL)
    return RedisStorage(redis)
