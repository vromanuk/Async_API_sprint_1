from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from core.config import FILM_CACHE_EXPIRE_IN_SECONDS
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.genre import Genre


@dataclass
class GenreService:
    redis: Redis
    elastic: AsyncElasticsearch

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def _get_genres_from_elastic(self, es_query: Optional[dict] = None) -> Optional[list[Genre]]:
        if es_query:
            doc = await self.elastic.search(
                index="genres",
                body=es_query["query"],
                sort=es_query["sort"],
                size=es_query["limit"],
                from_=es_query["from"],
                _source=es_query["source"],
            )
        else:
            doc = await self.elastic.search(
                index="genres",
            )
        return [Genre(**genre["_source"]) for genre in doc]

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        doc = await self.elastic.get("genres", genre_id)
        return Genre(**doc["_source"])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None

        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(genre.id, genre.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _put_genres_to_cache(self, genres: list[Genre]):
        await self.redis.set("genres", genres, expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _genres_from_cache(self) -> Optional[list[Genre]]:
        data = await self.redis.get("genres")
        if not data:
            return None

        genres = [Genre.parse_raw(genre) for genre in data]
        return genres

    async def get_genres(self, es_query: Optional[dict] = None) -> Optional[list[Genre]]:
        genres = await self._genres_from_cache()
        if not genres:
            genres = await self._get_genres_from_elastic(es_query)
            if not genres:
                return None
            await self._put_genres_to_cache(genres)

        return genres


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),  # noqa B008
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> GenreService:
    return GenreService(redis, elastic)
