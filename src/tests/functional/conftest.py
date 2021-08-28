from dataclasses import dataclass

import pytest
from elasticsearch import AsyncElasticsearch
from httpx import AsyncClient
from multidict import CIMultiDictProxy

from src.core.config import API_V1_PREFIX
from src.main import app


@dataclass
class HTTPResponse:
    request_url: str
    headers: CIMultiDictProxy[str]
    status: int
    body: dict

    @property
    def ok(self):
        return self.status // 200 == 1


@pytest.fixture(scope="session")
async def es_client():
    client = AsyncElasticsearch(hosts="127.0.0.1:9200")
    yield client
    await client.close()


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url=f"http://{API_V1_PREFIX}") as async_client:
        yield async_client
