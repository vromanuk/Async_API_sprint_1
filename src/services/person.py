from functools import lru_cache
from typing import List, Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.person import Person
from services.base import BaseService


class PersonService(BaseService):
    async def get_by_id(self, person_id: str) -> Optional[Person]:
        key = f"person_{person_id}"
        person = await self.get_from_cache_scalar(key)
        if not person:
            person = await self.get_from_elastic_scalar(person_id)
            if not person:
                return None
            await self.cache(key, person.json())

        return person

    async def get_list(self, redis_key: str, es_query: Optional[dict] = None) -> Optional[list[Person]]:
        people = await self.get_from_cache_many(redis_key)
        if not people:
            people = await self.get_from_elastic_many(es_query)
            if not people:
                return None
            await self.cache(redis_key, people)

        return people

    async def get_from_elastic_many(self, es_query: Optional[dict] = None) -> Optional[list[Person]]:
        if es_query:
            doc = await self.elastic.search(
                index="people",
                body=es_query["query"],
                sort=es_query["sort"],
                size=es_query["limit"],
                from_=es_query["from"],
                _source=es_query["source"],
            )
        else:
            doc = await self.elastic.search(
                index="people",
            )
        return [Person(**person["_source"]) for person in doc]

    async def get_from_elastic_scalar(self, person_id: str) -> Optional[Person]:
        doc = await self.elastic.get("people", person_id)
        return Person(**doc["_source"])

    async def get_from_cache_scalar(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def get_from_cache_many(self, key: str) -> Optional[List[Person]]:
        data = await self.redis.get(key)
        if not data:
            return None

        people = [Person.parse_raw(person) for person in data]
        return people


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),  # noqa B008
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> PersonService:
    return PersonService(redis, elastic)
