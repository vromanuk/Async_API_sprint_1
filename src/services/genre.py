from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from constants import FILM_CACHE_EXPIRE_IN_SECONDS
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


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),  # noqa B008
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> GenreService:
    return GenreService(redis, elastic)
