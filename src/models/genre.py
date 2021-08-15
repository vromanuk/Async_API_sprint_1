import datetime

import orjson
from pydantic import BaseModel
from utils import orjson_dumps


class Genre(BaseModel):
    id: str
    genre: str
    created: datetime.datetime
    modified: datetime.datetime

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
