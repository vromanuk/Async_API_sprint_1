from functools import lru_cache

from pydantic import BaseSettings, Field

from src.core.config import API_V1_PREFIX


class TestSettings(BaseSettings):
    base_url: str = Field(f"http://{API_V1_PREFIX}", env="BASE_URL")
    es_host: str = Field("http://127.0.0.1:9200", env="ELASTIC_HOST")
    redis_host: str = "localhost"
    redis_port: int = 6379

    class Config:
        env_file = ".env-tests"


@lru_cache()
def get_settings():
    return TestSettings()
