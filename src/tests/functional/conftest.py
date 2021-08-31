import json
from dataclasses import dataclass
from pathlib import Path

import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from httpx import AsyncClient
from multidict import CIMultiDictProxy

from src.db import elastic, redis
from src.main import app
from src.tests.functional.settings import TestSettings, get_settings


def load_params_from_json(json_path):
    script_location = Path(__file__).absolute().parent
    file_location = script_location / json_path
    with open(file_location) as f:
        return json.load(f)


@dataclass
class HTTPResponse:
    request_url: str
    headers: CIMultiDictProxy[str]
    status: int
    body: dict

    @property
    def ok(self):
        return self.status // 200 == 1


@pytest.fixture
async def es_client(settings: TestSettings):
    client = AsyncElasticsearch(hosts=settings.es_host)
    yield client
    await client.close()


@pytest.fixture()
async def setup(settings: TestSettings):
    elastic.es = AsyncElasticsearch(hosts=[settings.es_host])
    redis.redis = await aioredis.create_redis_pool((settings.redis_host, settings.redis_port), minsize=10, maxsize=20)
    yield


@pytest.fixture
async def client(setup, settings: TestSettings):
    async with AsyncClient(app=app, base_url=settings.base_url) as async_client:
        yield async_client


@pytest.fixture
async def settings():
    return get_settings()


@pytest.fixture
async def populate_es(es_client):
    movies_raw = load_params_from_json("fixtures/initial_data.json")

    await es_client.indices.create("movies")

    for movie in movies_raw:
        await es_client.index(index="movies", id=movie["id"], body=movie)

    yield

    await es_client.indices.delete(index="movies")
