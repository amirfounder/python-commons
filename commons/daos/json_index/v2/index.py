from typing import Generic, TypeVar, Optional

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from .models import JsonIndexModel


_K = TypeVar('_K')
_V = TypeVar('_V')


class JsonIndex(GenericModel, Generic[_K, _V]):
    source: dict[_K, _V] = Field(default={})

    def __contains__(self, item) -> bool:
        return item in self.source

    def __getitem__(self, item) -> _V:
        return self.source[item]

    def __setitem__(self, key, value) -> None:
        self.source[key] = value

    def get(self, key, default=None) -> Optional[_V]:
        return self.source.get(key, default)
