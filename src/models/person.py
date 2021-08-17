import datetime
from uuid import UUID

import orjson
from pydantic import BaseModel
from utils import orjson_dumps


class Person(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    birth_date: datetime.date
    created: datetime.datetime
    modified: datetime.datetime

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
