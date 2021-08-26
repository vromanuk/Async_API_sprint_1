from abc import ABC, abstractmethod
from typing import Optional

from elasticsearch import AsyncElasticsearch


class BaseService(ABC):
    def __init__(self, elastic: AsyncElasticsearch):
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
    async def get_list(self, es_query: Optional[dict] = None):
        pass
