from __future__ import annotations
from abc import ABC
from typing import Callable, Generator, Tuple

from commons.util import get_attributes


DEFAULT_TO_JSONABLE_FNS = {}
DEFAULT_FROM_JSONABLE_FNS = {}


def set_default_jsonable_loaders(
        type_: type,
        to_jsonable_type_loader: Callable,
        from_jsonable_type_loader: Callable
):
    DEFAULT_TO_JSONABLE_FNS[type_] = to_jsonable_type_loader
    DEFAULT_FROM_JSONABLE_FNS[type_] = from_jsonable_type_loader


def is_model_type(o: type):
    return issubclass(o, AbstractJsonModel)


def is_model(o):
    return isinstance(o, AbstractJsonModel)


def is_key_type(o: type):
    return issubclass(o, AbstractJsonModelKey)


def is_key(o):
    return isinstance(o, AbstractJsonModelKey)


class AbstractJsonModelKey:
    @property
    def can_load_to_jsonable_type(self):
        return self.load_to_jsonable_type is not None
    
    @property
    def can_load_from_jsonable_type(self):
        return self.load_from_jsonable_type is not None
    
    def __init__(self, type_: type, default=None, load_to_jsonable_type=None, load_from_jsonable_type=None):
        self.type = type_
        self.default = default
        self.load_to_jsonable_type = load_to_jsonable_type
        self.load_from_jsonable_type = load_from_jsonable_type
        self.value = None
        self.name = None
        self.set_model_defaults()

    def set_model_defaults(self):
        if is_model_type(self.type) and not self.default:
            self.default = self.type()

        if not self.load_to_jsonable_type:
            if self.type in DEFAULT_TO_JSONABLE_FNS:
                self.load_to_jsonable_type = DEFAULT_TO_JSONABLE_FNS[self.type]
            if is_model_type(self.type):
                self.load_to_jsonable_type = lambda o: dict(o)

        if not self.load_from_jsonable_type:
            if self.type in DEFAULT_FROM_JSONABLE_FNS:
                self.load_from_jsonable_type = DEFAULT_FROM_JSONABLE_FNS[self.type]
            if is_model_type(self.type):
                self.load_from_jsonable_type = lambda o: self.type(**o)


class AbstractJsonModel(ABC):
    _model_key_map = {}

    def get_key_map(self) -> Generator[Tuple[str, AbstractJsonModelKey], None, None]:
        for name, key in self._model_key_map[type(self)].items():
            yield name, key

    def get_keys(self) -> Generator[AbstractJsonModelKey, None, None]:
        for _, key in self.get_key_map():
            yield key

    def __init__(self, **kwargs):
        for key in self.get_keys():
            if key.name in kwargs:
                value = kwargs[key.name]
                if value and key.can_load_from_jsonable_type:
                    value = key.load_from_jsonable_type(value)
            else:
                value = key.default
            setattr(self, key.name, value)
            key.value = value

    def __init_subclass__(cls, **kwargs):
        cls._model_key_map[cls] = {}
        for name, attribute in get_attributes(cls):
            if is_key(attribute):
                attribute.name = name
                cls._model_key_map[cls][name] = attribute

    def __iter__(self):
        for key in self.get_keys():
            value = getattr(self, key.name)
            if value and key.can_load_to_jsonable_type:
                yield key.name, key.load_to_jsonable_type(value)
            else:
                yield key.name, value
