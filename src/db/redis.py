from functools import lru_cache

from aioredis import Redis

from src.services.base_cache import RedisCache

redis: Redis = None


@lru_cache()
async def get_redis() -> RedisCache:
    return RedisCache(redis)
