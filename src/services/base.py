from abc import ABC, abstractmethod
from typing import Optional, Union

from aioredis import Redis
from core.config import FILM_CACHE_EXPIRE_IN_SECONDS
from elasticsearch import AsyncElasticsearch


class BaseService(ABC):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @abstractmethod
    async def get_by_id(self, entity_id: str):
        pass

    @abstractmethod
    async def get_from_elastic_many(self, es_query: Optional[dict] = None):
        pass

    @abstractmethod
    async def get_from_elastic_scalar(self, entity_id: str):
        pass

    @abstractmethod
    async def get_from_cache(self, entity_id: Optional[str] = None):
        pass

    async def cache(self, key: str, data: Union[dict, list]):
        await self.redis.set(key, data, expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    @abstractmethod
    async def get_list(self, es_query: Optional[dict] = None):
        pass
