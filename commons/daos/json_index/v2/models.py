from datetime import datetime
from typing import Any

from pydantic import BaseModel

from commons.helpers import now


class JsonIndexModel(BaseModel):
    updated_at: datetime
    created_at: datetime

    def __init__(self, **data: Any):
        self.created_at = data.pop('created_at', now())
        self.updated_at = data.pop('updated_at', now())
        super().__init__(**data)
