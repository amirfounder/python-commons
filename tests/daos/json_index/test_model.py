from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from commons.daos.json_index import AbstractJsonIndex


class Index(AbstractJsonIndex):
    pass


class Recruiter(BaseModel):
    name: Optional[str]
    company: Optional[str]
    headline: Optional[str]
    username: Optional[str]
    last_contacted: Optional[datetime]


class Company(BaseModel):
    name: str
    url: str


def test_index_model_works():
    index = Index()
    index['amir'] = Recruiter(name='Amir', company=None, headline=None, username=None, last_contacted=None)
    index['dior'] = Recruiter(name='Dior', company=None, headline=None, username=None, last_contacted=None)

    j = index.json()
    i = Index.parse_raw(j)
    print(i)
