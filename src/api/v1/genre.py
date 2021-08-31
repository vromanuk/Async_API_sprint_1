from enum import Enum
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.constants import SortOrder
from src.models.genre import Genre
from src.services.genre import GenreService, get_genre_service
from src.utils import cached

router = APIRouter(
    prefix="/genres",
)


class SortFieldGenre(str, Enum):
    ID = "id"
    GENRE = "genre"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@router.get(
    "/",
    response_model=list[Genre],
    summary="Получение списка жанров",
    response_description="Список жанров",
)
@cached(decoder=Genre)
async def genre_list(
    search_query: Optional[str] = "",
    sort_order: SortOrder = SortOrder.ASC,
    sort: SortFieldGenre = SortFieldGenre.ID,
    page: int = 1,
    limit: int = 50,
    genre_service: GenreService = Depends(get_genre_service),  # noqa B008
) -> list[Genre]:
    sort_value = sort.value
    if sort_value == SortFieldGenre.GENRE.value:
        sort_value = f"{SortFieldGenre.GENRE.value}.raw"

    es_query = {
        "size": limit,
        "from": (page - 1) * limit,
        "sort": [f"{sort_value}:{sort_order.value}"],
        "_source": ["id", "genre"],
    }

    if search_query:
        es_query["query"] = {
            "multi_match": {
                "query": search_query,
                "fuzziness": "auto",
                "fields": ["genre^3"],
            }
        }

    return await genre_service.get_list(es_query)


@router.get(
    "/{genre_id}",
    response_model=Genre,
    summary="Получение информации о конкретном жанре",
    response_description="Информация о конкретном жанре",
)
@cached(decoder=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:  # noqa B008
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return genre
