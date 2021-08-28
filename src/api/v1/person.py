from enum import Enum
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.constants import SortOrder
from src.models.person import Person
from src.services.person import PersonService, get_person_service
from src.utils import cached

router = APIRouter(
    prefix="/people",
)


class SortFieldPerson(str, Enum):
    ID = "id"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@router.get(
    "/",
    response_model=list[Person],
    summary="Получение списка участников в произведении",
    response_description="Список участников в произведении",
)
@cached(decoder=Person)
async def people_list(
    search_query: Optional[str] = "",
    sort_order: SortOrder = SortOrder.ASC,
    sort: SortFieldPerson = SortFieldPerson.ID,
    page: int = 1,
    limit: int = 50,
    person_service: PersonService = Depends(get_person_service),  # noqa B008
) -> list[Person]:
    sort_value = sort.value
    if sort_value in [SortFieldPerson.FIRST_NAME.value, SortFieldPerson.LAST_NAME.value]:
        sort_value = f"{sort_value}.raw"

    es_query = {
        "size": limit,
        "from": (page - 1) * limit,
        "sort": [f"{sort_value}:{sort_order.value}"],
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

    return await person_service.get_list(es_query)


@router.get(
    "/{person_id}",
    response_model=Person,
    summary="Получение информации о конкретной личности",
    response_description="Информация о конкретной личности",
)
@cached(decoder=Person)
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
