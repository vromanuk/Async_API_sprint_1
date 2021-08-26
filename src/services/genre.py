from functools import lru_cache
from typing import Optional

from db.elastic import get_elastic
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from models.genre import Genre
from services.base import BaseService


class GenreService(BaseService):
    async def get_by_id(self, genre_id: str) -> Optional[Genre]:
        genre = await self.get_from_elastic_scalar(genre_id)
        if not genre:
            return None

        return genre

    async def get_list(self, es_query: Optional[dict] = None) -> list[Genre]:
        genres = await self.get_from_elastic_many(es_query)
        if genres is None:
            return []

        return genres

    async def get_from_elastic_many(self, es_query: Optional[dict] = None) -> Optional[list[Genre]]:
        if es_query:
            doc = await self.elastic.search(
                index="genres",
                body=es_query.get("query"),
                sort=es_query["sort"],
                size=es_query["size"],
                from_=es_query["from"],
                _source=es_query["_source"],
            )
        else:
            doc = await self.elastic.search(
                index="genres",
            )
        return [Genre(**genre["_source"]) for genre in doc]

    async def get_from_elastic_scalar(self, genre_id: str) -> Optional[Genre]:
        doc = await self.elastic.get("genres", genre_id)
        return Genre(**doc["_source"])


@lru_cache()
def get_genre_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> GenreService:
    return GenreService(elastic)
