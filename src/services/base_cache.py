from abc import ABC, abstractmethod
from typing import Optional, Union

from aioredis import Redis
from core.config import CACHE_TTL


class BaseCache(ABC):
    @abstractmethod
    async def cache(self, key: str, data: Union[dict, list]):
        pass

    @abstractmethod
    async def get_from_cache_scalar(self, entity_id: str):
        pass

    @abstractmethod
    async def get_from_cache_many(self, key: str):
        pass


class RedisCache(BaseCache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def cache(self, key: str, data: Union[dict, list]):
        await self.redis.set(key, data, expire=CACHE_TTL)

    async def get_from_cache_many(self, key: str) -> Optional[list]:
        data = await self.redis.get(key)
        if not data:
            return None

    async def get_from_cache_scalar(self, film_id: str):
        data = await self.redis.get(film_id)
        if not data:
            return None
