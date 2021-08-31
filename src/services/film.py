from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src.db.elastic import get_elastic
from src.models.film import Film
from src.services.base import BaseService


class FilmService(BaseService):
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self.get_from_elastic_scalar(film_id)
        if not film:
            return None

        return film

    async def get_list(self, es_query: Optional[dict] = None) -> list[Film]:
        films = await self.get_from_elastic_many(es_query)
        if films is None:
            return []

        return films

    async def get_from_elastic_scalar(self, film_id: str) -> Optional[Film]:
        doc = await self.elastic.get("movies", film_id)
        return Film(**doc["_source"])

    async def get_from_elastic_many(self, es_query: Optional[dict] = None) -> Optional[list[Film]]:
        if es_query:
            doc = await self.elastic.search(
                index="movies",
                body=es_query.get("query"),
                sort=es_query["sort"],
                size=es_query["size"],
                from_=es_query["from"],
                _source=es_query["_source"],
            )
        else:
            doc = await self.elastic.search(
                index="movies",
            )
        return [Film(**film["_source"]) for film in doc["hits"]["hits"]]


@lru_cache()
def get_film_service(
    elastic: AsyncElasticsearch = Depends(get_elastic),  # noqa B008
) -> FilmService:
    return FilmService(elastic)
