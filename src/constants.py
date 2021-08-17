from enum import Enum

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"
