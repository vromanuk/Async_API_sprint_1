from enum import Enum
from http import HTTPStatus
from typing import Optional

from constants import SortOrder
from fastapi import APIRouter, Depends, HTTPException
from models.film import Film
from services.film import FilmService, get_film_service

router = APIRouter(
    prefix="/films",
)


class SortFieldFilm(str, Enum):
    ID = "id"
    TITLE = "title"
    IMDB_RATING = "imdb_rating"


@router.get("/", response_model=list[Film])
async def film_list(
    search_query: Optional[str] = None,
    sort_order: SortOrder = SortOrder.ASC,
    sort: SortFieldFilm = SortFieldFilm.ID,
    page: int = 1,
    limit: int = 50,
    film_service: FilmService = Depends(get_film_service),  # noqa B008
) -> list[Film]:
    redis_key = f"{sort_order.lower()}_{sort.lower()}_{page}_{limit}"
    sort_value = sort.value
    if sort_value == SortFieldFilm.TITLE.value:
        sort_value = f"{SortFieldFilm.TITLE.value}.raw"

    es_query = {
        "size": limit,
        "from": (page - 1) * limit,
        "sort": [{sort_value: sort_order.value}],
        "_source": ["id", "title", "imdb_rating"],
    }

    if search_query:
        es_query["query"] = {
            "multi_match": {
                "query": search_query,
                "fuzziness": "auto",
                "fields": ["title^5", "description^4", "genre^3", "actors_names^3", "writers_names^2", "director"],
            }
        }

    films = await film_service.get_list(redis_key, es_query)
    if not films:
        return []

    return films


@router.get("/{film_id}", response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:  # noqa B008
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return Film(id=film.id, title=film.title)
