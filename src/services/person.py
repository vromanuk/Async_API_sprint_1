from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src.db.elastic import get_elastic
from src.models.person import Person
from src.services.base import BaseService


class PersonService(BaseService):
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self.get_from_elastic_scalar(person_id)
        if not person:
            return None

        return person

    async def get_list(self, es_query: Optional[dict] = None) -> list[Person]:
        people = await self.get_from_elastic_many(es_query)
        if people is None:
            return []

        return people

    async def get_from_elastic_many(self, es_query: Optional[dict] = None) -> Optional[list[Person]]:
        if es_query:
            doc = await self.elastic.search(
                index="people",
                body=es_query.get("query"),
                sort=es_query["sort"],
                size=es_query["size"],
                from_=es_query["from"],
                _source=es_query["_source"],
            )
        else:
            doc = await self.elastic.search(
                index="people",
            )
        return [Person(**person["_source"]) for person in doc["hits"]["hits"]]

    async def get_from_elastic_scalar(self, person_id: str) -> Optional[Person]:
        doc = await self.elastic.get("people", person_id)
        return Person(**doc["_source"])


@lru_cache()
def get_person_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> PersonService:
    return PersonService(elastic)
