from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from models.person import Person
from services.person import PersonService, get_person_service

router = APIRouter(
    prefix="/people",
)


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
