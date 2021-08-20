from api.v1 import film, genre, person
from main import app

app.include_router(film.router, prefix="/v1", tags=["film"])
app.include_router(genre.router, prefix="/v1", tags=["genre"])
app.include_router(person.router, prefix="/v1", tags=["person"])
