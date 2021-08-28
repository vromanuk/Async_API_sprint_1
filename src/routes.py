from fastapi import APIRouter

from src.api.v1 import film, genre, person, smoke

api_router = APIRouter()

api_router.include_router(film.router, tags=["film"])
api_router.include_router(genre.router, tags=["genre"])
api_router.include_router(person.router, tags=["person"])
api_router.include_router(smoke.router, tags=["smoke"])
