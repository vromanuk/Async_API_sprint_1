import pytest
from httpx import AsyncClient

from src.models.film import Film


@pytest.mark.asyncio
async def test_film_list(client: AsyncClient):
    film_list_url = "/films/"
    # Fetch data from elastic
    response = await client.get(film_list_url)
    resp_json = response.json()

    assert response.status_code == 200
    assert resp_json != []
    assert all(isinstance(Film.parse_obj(film), Film) for film in resp_json)

    # Fetch data from cache
    response = await client.get(film_list_url)
    resp_json = response.json()

    assert response.status_code == 200
    assert resp_json != []
    assert all(isinstance(Film.parse_obj(film), Film) for film in resp_json)


@pytest.mark.asyncio
async def test_film_details(client: AsyncClient):
    film_details_url = "/films/1"
    # Fetch data from elastic
    response = await client.get(film_details_url)
    resp_json = response.json()

    assert response.status_code == 200
    assert resp_json != []
    assert isinstance(Film.parse_obj(resp_json), Film)

    # Fetch data from cache
    response = await client.get(film_details_url)
    resp_json = response.json()

    assert response.status_code == 200
    assert resp_json != []
    assert isinstance(Film.parse_obj(resp_json), Film)
