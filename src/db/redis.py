from aioredis import Redis

from src.services.base_cache import RedisCache

redis: Redis = None


async def get_redis() -> RedisCache:
    return RedisCache(redis)
