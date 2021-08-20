from functools import lru_cache
from typing import List, Optional, Union

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.genre import Genre
from services.base import BaseService


class GenreService(BaseService):
    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        key = f"genre_{genre_id}"
        genre = await self.get_from_cache(key)
        if not genre:
            genre = await self.get_from_elastic_scalar(genre_id)
            if not genre:
                return None
            await self.cache(key, genre.json())

        return genre

    async def get_list(self, es_query: Optional[dict] = None) -> Optional[list[Genre]]:
        genres = await self.get_from_cache()
        if not genres:
            genres = await self.get_from_elastic_many(es_query)
            if not genres:
                return None
            await self.cache("genres", genres)

        return genres

    async def get_from_elastic_many(self, es_query: Optional[dict] = None) -> Optional[list[Genre]]:
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

    async def get_from_elastic_scalar(self, genre_id: str) -> Optional[Genre]:
        doc = await self.elastic.get("genres", genre_id)
        return Genre(**doc["_source"])

    async def get_from_cache(self, genre_id: Optional[str] = None) -> Optional[Union[Genre, List[Genre]]]:
        if genre_id:
            data = await self.redis.get(genre_id)
            if not data:
                return None

            genre = Genre.parse_raw(data)
            return genre
        data = await self.redis.get("genres")
        if not data:
            return None

        genres = [Genre.parse_raw(genre) for genre in data]
        return genres


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),  # noqa B008
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> GenreService:
    return GenreService(redis, elastic)
