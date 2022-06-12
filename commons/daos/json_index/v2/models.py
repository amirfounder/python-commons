from datetime import datetime
from uuid import uuid4, UUID

from pydantic import BaseModel, validator, Field

from commons.helpers import now, format_iso, parse_iso


class JsonIndexModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    updated_at: datetime = Field(default_factory=now)
    created_at: datetime = Field(default_factory=now)

    class Config:
        json_encoders = {
            datetime: format_iso,
            UUID: lambda v: str(v)
        }

    @classmethod
    @validator('*', pre=True)
    def parse_datetimes(cls, value):
        try:
            return parse_iso(value)
        except Exception:
            return value
