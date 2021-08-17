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

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        doc = await self.elastic.get("people", person_id)
        return Person(**doc["_source"])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(person.id, person.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),  # noqa B008
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> PersonService:
    return PersonService(redis, elastic)
