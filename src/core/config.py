import os

PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

ELASTIC_HOST = os.getenv("ELASTIC_HOST", "es01")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
