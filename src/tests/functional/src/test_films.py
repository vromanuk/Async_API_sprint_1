from asyncio import sleep

import pytest
from elasticsearch import NotFoundError
from httpx import AsyncClient

from src.models.film import Film, MovieType


@pytest.mark.asyncio
async def test_film_list(client: AsyncClient):
    film_list_url = "/films/"
    await sleep(0.5)
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
    film: Film = Film.parse_obj(response.json())

    assert response.status_code == 200
    assert film.title == "Beirut"
    assert film.type == MovieType.TV_SHOW
    assert isinstance(film, Film)

    # Fetch data from cache
    response = await client.get(film_details_url)
    resp_json = response.json()

    assert response.status_code == 200
    assert resp_json != []
    assert isinstance(Film.parse_obj(resp_json), Film)


@pytest.mark.asyncio
async def test_film_details_404(client: AsyncClient):
    film_details_url = "/films/-1"
    with pytest.raises(NotFoundError):
        response = await client.get(film_details_url)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_film_list_wrong_sort_field(client: AsyncClient):
    film_list_url = "/films/?sort=None"
    response = await client.get(film_list_url)
    resp_json = response.json()
    assert response.status_code == 422
    assert "value is not a valid enumeration member" in resp_json["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_film_list_wrong_order_field(client: AsyncClient):
    film_list_url = "/films/?sort_order=None"
    response = await client.get(film_list_url)
    resp_json = response.json()
    assert response.status_code == 422
    assert "value is not a valid enumeration member" in resp_json["detail"][0]["msg"]


@pytest.mark.asyncio
async def test_film_list_limit(client: AsyncClient):
    film_list_url = "/films/"
    await sleep(0.5)
    response = await client.get(f"{film_list_url}?page=1&limit=2")
    resp_json = response.json()

    assert response.status_code == 200
    assert len(resp_json) == 2
    assert resp_json[1]["title"] == "2046"

    response = await client.get(f"{film_list_url}?page=2&limit=2")
    resp_json = response.json()

    assert response.status_code == 200
    assert len(resp_json) == 2
    assert resp_json[0]["title"] == "From Paris with Love"
