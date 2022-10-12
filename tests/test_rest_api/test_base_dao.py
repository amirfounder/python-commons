from typing import Optional
from unittest import TestCase

from sqlalchemy import String, Column, create_engine, Integer, ForeignKey
from sqlalchemy.engine import URL
from sqlalchemy.orm import relationship

from commons.rest_api.base_dao import BaseDao
from commons.rest_api.base_model import BaseDBModel, BaseBLModel, Base
from commons.rest_api.db import drop_create_public_schema, sync_model_tables


class BookDBModel(BaseDBModel):
    __tablename__ = 'books'
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, nullable=False)
    libraries = relationship('LibraryDBModel', secondary='books_libraries')


class BookBLModel(BaseBLModel):
    title: str
    author: str
    isbn: str
    libraries: Optional[list]


class LibraryDBModel(BaseDBModel):
    __tablename__ = 'libraries'
    name = Column(String, nullable=False)
    books = relationship('BookDBModel', secondary='books_libraries')


class LibraryBLModel(BaseBLModel):
    name: str
    books: Optional[list]

class BooksLibrariesDBModel(BaseDBModel):
    __tablename__ = 'books_libraries'
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    library_id = Column(Integer, ForeignKey('libraries.id'), nullable=False)


class BoosLibrariesBLModel(BaseBLModel):
    book_id: int
    library_id: int


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


class LibraryDao(BaseDao):
    def __init__(self):
        super().__init__(
            db_model_class=LibraryDBModel,
            bl_model_class=LibraryBLModel,
            engine=engine
        )


class BooksLibrariesDao(BaseDao):
    def __init__(self):
        super().__init__(
            db_model_class=BooksLibrariesDBModel,
            bl_model_class=BoosLibrariesBLModel,
            engine=engine
        )


class TestBaseDao(TestCase):
    def test_get_all_paginated(self):
        drop_create_public_schema(engine)
        sync_model_tables(engine, [BookDBModel, LibraryDBModel, BooksLibrariesDBModel])
        books = BookDao()
        books.create(BookBLModel(title='title1', author='author1', isbn='isbn1'))
        books.create(BookBLModel(title='title2', author='author2', isbn='isbn2'))
        books.create(BookBLModel(title='title3', author='author3', isbn='isbn3'))
        libraries = LibraryDao()
        libraries.create(LibraryBLModel(name='library1'))
        libraries.create(LibraryBLModel(name='library2'))
        libraries.create(LibraryBLModel(name='library3'))
        books_libraries = BooksLibrariesDao()
        books_libraries.create(BoosLibrariesBLModel(book_id=1, library_id=1))
        books_libraries.create(BoosLibrariesBLModel(book_id=1, library_id=2))
        books_libraries.create(BoosLibrariesBLModel(book_id=2, library_id=2))
        books_libraries.create(BoosLibrariesBLModel(book_id=3, library_id=3))
        result = books.get_all(exclude_columns=[BookDBModel.created_at, 'updated_at'])
        print(result)
