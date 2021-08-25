from enum import Enum
from http import HTTPStatus
from typing import Optional

from constants import SortOrder
from fastapi import APIRouter, Depends, HTTPException
from models.person import Person
from services.person import PersonService, get_person_service

router = APIRouter(
    prefix="/people",
)


class SortFieldPerson(str, Enum):
    ID = "id"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"


@router.get("/", response_model=list[Person])
async def people_list(
    search_query: Optional[str] = None,
    sort_order: SortOrder = SortOrder.ASC,
    sort: SortFieldPerson = SortFieldPerson.ID,
    page: int = 1,
    limit: int = 50,
    person_service: PersonService = Depends(get_person_service),  # noqa B008
) -> list[Person]:
    cache_key = f"{search_query}:{sort_order.lower()}:{sort.lower()}:{page}:{limit}"
    sort_value = sort.value
    if sort_value in [SortFieldPerson.FIRST_NAME.value, SortFieldPerson.LAST_NAME.value]:
        sort_value = f"{sort_value}.raw"

    es_query = {
        "size": limit,
        "from": (page - 1) * limit,
        "sort": [{sort_value: sort_order.value}],
        "_source": ["id", "first_name", "last_name"],
    }

    if search_query:
        es_query["query"] = {
            "multi_match": {
                "query": search_query,
                "fuzziness": "auto",
                "fields": ["first_name^2", "last_name^2"],
            }
        }

    return await person_service.get_list(cache_key, es_query)


@router.get("/{person_id}", response_model=Person)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)  # noqa B008
) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return Person(
        id=person.id,
        first_name=person.first_name,
        last_name=person.last_name,
        birth_date=person.birth_date,
        created=person.created,
        modified=person.modified,
    )
