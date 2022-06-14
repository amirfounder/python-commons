from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, TypeVar

from commons.daos import JsonIndexModel, JsonIndex


class Recruiter(JsonIndexModel):
    name: Optional[str]
    company: Optional[str]
    headline: Optional[str]
    username: Optional[str]
    last_contacted: Optional[datetime]


class Company(JsonIndexModel):
    name: str
    url: str


K = TypeVar('K', bound=str)
V = TypeVar('V', bound=Recruiter)


def test_index_model_works():
    index = JsonIndex(Recruiter, 'data/index.json', {'flush_after_set': True})
    preset_uuid = uuid.uuid4()

    index['amir'] = Recruiter(id=preset_uuid, name='Amir')
    index['dior'] = Recruiter(name='Dior')
    index.flush()
    index.load()

    print(index)
