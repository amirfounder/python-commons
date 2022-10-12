from datetime import datetime
from typing import Dict, List, Optional, Callable

from pydantic import Extra, BaseModel
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import registry as _registry, InstrumentedAttribute

from commons.datetime import now

registry = _registry()
Base = registry.generate_base()


class BaseBLModel(BaseModel):
    id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        orm_mode = True
        extra = Extra.ignore


class BaseDBModel(Base):
    __abstract__ = True
    __tablename__: str

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(True), default=now)
    updated_at = Column(DateTime(True), default=now)
    deleted_at = Column(DateTime(True), default=None)

    def __init__(self, **kwargs):
        now_ = now()
        self.created_at = now_
        self.updated_at = now_
        self.merge_dict(kwargs)
        super().__init__()

    @classmethod
    def has_column(cls, column_name: str) -> bool:
        return column_name in cls.get_column_names()

    @classmethod
    def get_column(cls, column_name: str):
        return cls.__table__.columns.get(column_name)

    @classmethod
    def get_columns(cls) -> List[Column]:
        return [c for c in cls.get_table().columns]

    @classmethod
    def get_column_names(cls) -> List[str]:
        return [c.name for c in cls.get_columns()]

    @classmethod
    def get_columns_with_fks(cls) -> List[Column]:
        return [c for c in cls.get_columns() if c.foreign_keys]

    @classmethod
    def get_table(cls):
        return Base.metadata.tables.get(cls.__tablename__)

    @classmethod
    def get_instrumented_attributes(cls, filters: List[Callable[[InstrumentedAttribute], bool]] = None) -> \
            List[InstrumentedAttribute]:
        attributes = []

        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name)
            if isinstance(attribute, InstrumentedAttribute):
                for filter_ in filters:
                    if not filter_(attribute):
                        continue
                attributes.append(attribute)

        return attributes

    @classmethod
    def get_instrumented_attribute_by_name(cls, attribute_name: str, hard_fail: bool = True):
        res = getattr(cls, attribute_name)
        if isinstance(res, InstrumentedAttribute):
            return res
        if hard_fail:
            raise AttributeError(f'Attribute {attribute_name} is not an InstrumentedAttribute')

    @classmethod
    def has_instrumented_attribute_by_name(cls, attribute_name: str):
        attr = getattr(cls, attribute_name, None)
        return isinstance(attr, InstrumentedAttribute)

    @classmethod
    def clean_obj(cls, obj: Dict) -> None:
        kv = list(obj.items())
        names = cls.get_column_names()
        for k, v in kv:
            if k not in names:
                del obj[k]

    def merge_dict(self, obj: Dict):
        self.clean_obj(obj)
        for k, v in obj.items():
            setattr(self, k, v)

    @classmethod
    def from_dict(cls, obj: Dict):
        instance = cls()
        instance.merge_dict(obj)
        return instance

    def to_dict(self):
        d = {}
        for c in self.get_columns():
            if v := getattr(self, c.name, None):
                d[c.name] = v
        return d
