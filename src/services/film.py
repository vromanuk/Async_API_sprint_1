from functools import lru_cache
from typing import List, Optional, Union

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film
from services.base import BaseService


class FilmService(BaseService):
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        key = f"film_{film_id}"
        film = await self.get_from_cache(key)
        if not film:
            film = await self.get_from_elastic_scalar(film_id)
            if not film:
                return None
            await self.cache(key, film.json())

        return film

    async def get_list(self, es_query: Optional[dict] = None) -> Optional[list[Film]]:
        films = await self.get_from_cache()
        if not films:
            films = await self.get_from_elastic_many(es_query)
            if not films:
                return None
            await self.cache("films", films)

        return films

    async def get_from_elastic_scalar(self, film_id: str) -> Optional[Film]:
        doc = await self.elastic.get("movies", film_id)
        return Film(**doc["_source"])

    async def get_from_elastic_many(self, es_query: Optional[dict] = None) -> Optional[list[Film]]:
        if es_query:
            doc = await self.elastic.search(
                index="movies",
                body=es_query["query"],
                sort=es_query["sort"],
                size=es_query["limit"],
                from_=es_query["from"],
                _source=es_query["source"],
            )
        else:
            doc = await self.elastic.search(
                index="movies",
            )
        return [Film(**film["_source"]) for film in doc]

    async def get_from_cache(self, film_id: Optional[str] = None) -> Optional[Union[Film, List[Film]]]:
        if film_id:
            data = await self.redis.get(film_id)
            if not data:
                return None

            film = Film.parse_raw(data)
            return film
        data = await self.redis.get("films")
        if not data:
            return None

        films = [Film.parse_raw(film) for film in data]
        return films


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),  # noqa B008
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> FilmService:
    return FilmService(redis, elastic)
