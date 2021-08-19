from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from core.config import FILM_CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.film import Film


@dataclass
class FilmService:
    redis: Redis
    elastic: AsyncElasticsearch

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        doc = await self.elastic.get("movies", film_id)
        return Film(**doc["_source"])

    async def _get_films_from_elastic(self, es_query: Optional[dict] = None) -> Optional[list[Film]]:
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

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _films_from_cache(self) -> Optional[list[Film]]:
        data = await self.redis.get("films")
        if not data:
            return None

        films = [Film.parse_raw(film) for film in data]
        return films

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _put_films_to_cache(self, films: list[Film]):
        await self.redis.set("films", films, expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_films(self, es_query: Optional[dict] = None) -> Optional[list[Film]]:
        films = await self._films_from_cache()
        if not films:
            films = await self._get_films_from_elastic(es_query)
            if not films:
                return None
            await self._put_films_to_cache(films)

        return films


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),  # noqa B008
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> FilmService:
    return FilmService(redis, elastic)
