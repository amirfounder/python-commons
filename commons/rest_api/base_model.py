from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Extra, BaseModel
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import registry as _registry

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
        self.from_dict(kwargs)
        super().__init__()

    @classmethod
    def has_column(cls, column_name: str) -> bool:
        return column_name in cls.get_column_names()

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
    def clean_obj(cls, obj: Dict) -> None:
        kv = list(obj.items())
        names = cls.get_column_names()
        for k, v in kv:
            if k not in names:
                del obj[k]

    def from_dict(self, obj: Dict):
        self.clean_obj(obj)
        for k, v in obj.items():
            setattr(self, k, v)

    def to_dict(self):
        d = {}
        for c in self.get_columns():
            if v := getattr(self, c.name, None):
                d[c.name] = v
        return d
