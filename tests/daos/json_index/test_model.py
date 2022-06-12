from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, TypeVar

from commons.daos.json_index import JsonIndexModel
from commons.daos.json_index.v2.index import JsonIndexBuilder


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


index = JsonIndexBuilder()\
        .set_model(Recruiter)\
        .set_path('dummy-data/index.json')\
        .set_configs({'flush_after_set': True})\
        .build()


def test_index_model_works():
    preset_uuid = uuid.uuid4()

    index['amir'] = Recruiter(id=preset_uuid, name='Amir')
    index['dior'] = Recruiter(name='Dior')
    index.flush()
    index.load()

    print(index)
