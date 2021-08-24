from abc import ABC, abstractmethod
from typing import Optional, Union

from elasticsearch import AsyncElasticsearch
from services.base_cache import BaseCache


class BaseService(ABC):
    def __init__(self, cache: BaseCache, elastic: AsyncElasticsearch):
        self.cache = cache
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
    async def get_from_cache_scalar(self, entity_id: str):
        pass

    @abstractmethod
    async def get_from_cache_many(self, key: str):
        pass

    async def cache(self, key: str, data: Union[dict, list]):
        await self.cache.cache(key, data)

    @abstractmethod
    async def get_list(self, redis_key: str, es_query: Optional[dict] = None):
        pass
