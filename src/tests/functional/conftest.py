from dataclasses import dataclass

import pytest
from elasticsearch import AsyncElasticsearch
from httpx import AsyncClient
from multidict import CIMultiDictProxy

from src.main import app
from src.tests.functional.settings import TestSettings, get_settings


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
async def es_client(settings: TestSettings):
    client = AsyncElasticsearch(hosts=settings.es_host)
    yield client
    await client.close()


@pytest.fixture
async def client(settings: TestSettings):
    async with AsyncClient(app=app, base_url=settings.base_url) as async_client:
        yield async_client


@pytest.fixture
async def settings():
    return get_settings()
