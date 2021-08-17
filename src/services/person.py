from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from constants import FILM_CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.person import Person


@dataclass
class PersonService:
    redis: Redis
    elastic: AsyncElasticsearch

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def _get_people_from_elastic(self, es_query: Optional[dict] = None) -> Optional[list[Person]]:
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

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        doc = await self.elastic.get("people", person_id)
        return Person(**doc["_source"])

    async def _people_from_cache(self) -> Optional[list[Person]]:
        data = await self.redis.get("people")
        if not data:
            return None

        people = [Person.parse_raw(person) for person in data]
        return people

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_people_to_cache(self, people: list[Person]):
        await self.redis.set("people", people, expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(person.id, person.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_people(self, es_query: Optional[dict] = None) -> Optional[list[Person]]:
        people = await self._people_from_cache()
        if not people:
            people = await self._get_people_from_elastic(es_query)
            if not people:
                return None
            await self._put_people_to_cache(people)

        return people


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),  # noqa B008
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> PersonService:
    return PersonService(redis, elastic)
