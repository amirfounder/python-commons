from unittest import TestCase

from sqlalchemy import String, Column, create_engine
from sqlalchemy.engine import URL

from commons.rest_api.base_dao import BaseDao
from commons.rest_api.base_model import BaseDBModel, BaseBLModel, Base


class BookDBModel(BaseDBModel):
    __tablename__ = 'books'
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, nullable=False)


class BookBLModel(BaseBLModel):
    title: str
    author: str
    isbn: str


engine = create_engine(
    URL.create(
        drivername='postgresql',
        username='postgres',
        password='root',
        host='localhost',
        port=5432,
        database='commons_test_db'
    )
)


class BookDao(BaseDao):
    def __init__(self):
        super().__init__(
            db_model_class=BookDBModel,
            bl_model_class=BookBLModel,
            engine=engine
        )


class TestBaseDao(TestCase):
    def test_get_all_paginated(self):
        Base.metadata.create_all(bind=engine, tables=[BookDBModel.__table__])
        dao = BookDao()
        # dao.create(BookBLModel(title='title1', author='author1', isbn='isbn1'))
        # dao.create(BookBLModel(title='title2', author='author2', isbn='isbn2'))
        # dao.create(BookBLModel(title='title3', author='author3', isbn='isbn3'))
        dao.get_all(exclude_columns=[BookDBModel.created_at, 'updated_at'])
