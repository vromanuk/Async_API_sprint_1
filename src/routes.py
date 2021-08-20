from api.v1 import film, genre, person
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(film.router, tags=["film"])
api_router.include_router(genre.router, tags=["genre"])
api_router.include_router(person.router, tags=["person"])
