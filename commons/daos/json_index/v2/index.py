from __future__ import annotations
from typing import Generic, TypeVar, Optional, Any

from pydantic import Field, parse_obj_as
from pydantic.generics import GenericModel

from commons.helpers import safe_write_to_file, safe_read_json_as_obj_from_file

_K = TypeVar('_K')
_V = TypeVar('_V')


class JsonIndex(GenericModel, Generic[_K, _V]):
    source: dict[_K, _V] = Field(default={})
    _source_path: str
    _flush_after_set: bool = Field(default=False)

    @classmethod
    def build(cls):
        return cls.parse_file(cls._source_path)

    def __contains__(self, item) -> bool:
        return item in self.source

    def __getitem__(self, item) -> _V:
        return self.source[item]

    def __setitem__(self, key, value) -> None:
        self.source[key] = value
        if self._flush_after_set:
            self.flush()

    def get(self, key, default=None) -> Optional[_V]:
        return self.source.get(key, default)

    def flush(self):
        safe_write_to_file(self._source_path, self.json())

    def query(self, filter_: dict):
        # TODO -> Implement when needed
        pass
