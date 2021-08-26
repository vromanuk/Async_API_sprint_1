from abc import ABC, abstractmethod
from typing import Optional, Union

from aioredis import Redis

from src.core.config import CACHE_TTL


class BaseCache(ABC):
    @abstractmethod
    async def cache(self, key: str, data: Union[dict, list]):
        pass

    @abstractmethod
    async def get_from_cache(self, key: str):
        pass


class RedisCache(BaseCache):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def cache(self, key: str, data: Union[dict, bytes]):
        await self.redis.set(key, data, expire=CACHE_TTL)

    async def get_from_cache(self, key: str) -> Optional[bytes]:
        data = await self.redis.get(key)
        if not data:
            return None
        return data
