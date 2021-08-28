import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_film_list(client: AsyncClient):
    response = await client.get("/films/")

    assert response.status_code == 200
    assert response.json() == []
