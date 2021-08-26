from enum import Enum
from http import HTTPStatus
from typing import Optional

from constants import SortOrder
from fastapi import APIRouter, Depends, HTTPException
from models.genre import Genre
from services.genre import GenreService, get_genre_service
from utils import cached

router = APIRouter(
    prefix="/genres",
)


class SortFieldGenre(str, Enum):
    ID = "id"
    GENRE = "genre"


@router.get("/", response_model=list[Genre])
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
        "sort": [{sort_value: sort_order.value}],
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


@router.get("/{genre_id}", response_model=Genre)
@cached(decoder=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:  # noqa B008
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return Genre(id=genre.id, genre=genre.genre, created=genre.created, modified=genre.modified)
