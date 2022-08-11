from abc import ABC
from datetime import datetime
from uuid import uuid4, UUID

import orjson
from pydantic import BaseModel, validator, Field

from python_commons.helpers import now, format_iso, parse_iso


def orjson_dumps(o, *, default):
    return orjson.dumps(o, default=default).decode()


class AbstractKeyValueIndexModel(BaseModel, ABC):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        json_encoders = {
            datetime: format_iso,
            UUID: str
        }

    @classmethod
    @validator('updated_at', 'created_at', pre=True)
    def parse_datetimes(cls, value):
        return parse_iso(value)


class KeyValueIndexModel(AbstractKeyValueIndexModel):
    id: UUID = Field(default_factory=uuid4)
    updated_at: datetime = Field(default_factory=now)
    created_at: datetime = Field(default_factory=now)


class KeyValueIndexSubModel(AbstractKeyValueIndexModel):
    pass
