from __future__ import annotations
from abc import ABC
from typing import Callable

from commons.util import get_attributes


DEFAULT_TO_JSONABLE_FNS = {}
DEFAULT_FROM_JSONABLE_FNS = {}


def set_default_jsonable_fns(type_: type, to_jsonable: Callable, from_jsonable: Callable):
    DEFAULT_TO_JSONABLE_FNS[type_] = to_jsonable
    DEFAULT_FROM_JSONABLE_FNS[type_] = from_jsonable


def is_model_type(o: type):
    return issubclass(o, AbstractModel)


def is_model(o):
    return isinstance(o, AbstractModel)


def is_key_type(o: type):
    return issubclass(o, Key)


def is_key(o):
    return isinstance(o, Key)


class Key:
    def __init__(self, type_: type, default=None, to_jsonable=None, from_jsonable=None):
        self.type = type_
        self.default = default
        self.to_jsonable = to_jsonable
        self.from_jsonable = from_jsonable
        self.set_model_defaults()

    def set_model_defaults(self):
        if is_model_type(self.type) and not self.default:
            self.default = self.type()

        if self.type in DEFAULT_TO_JSONABLE_FNS:
            self.to_jsonable = DEFAULT_TO_JSONABLE_FNS[self.type]
        if is_model_type(self.type):
            self.to_jsonable = dict

        if self.type in DEFAULT_FROM_JSONABLE_FNS:
            self.from_jsonable = DEFAULT_FROM_JSONABLE_FNS[self.type]
        if is_model_type(self.type):
            self.from_jsonable = lambda o: self.type(**o)


class AbstractModel(ABC):
    _model_key_map = {}

    def __init__(self, **kwargs):
        t = type(self)
        for n, key in self._model_key_map[t].items():
            if n in kwargs:
                v = kwargs[n]
                if v and key.from_jsonable:
                    v = key.from_jsonable(v)
            else:
                v = key.default
            setattr(self, n, v)

    def __init_subclass__(cls, **kwargs):
        cls._model_key_map[cls] = {}
        for k, v in get_attributes(cls):
            if is_key(v):
                cls._model_key_map[cls][k] = v

    def __iter__(self):
        t = type(self)
        for n, key in self._model_key_map[t].items():
            v = getattr(self, n)
            if v and key.to_jsonable:
                yield n, key.to_jsonable(v)
            else:
                yield n, v
