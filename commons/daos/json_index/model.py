from abc import ABC
from datetime import datetime

from commons import parse_iso_dt
from commons.util import safe_cast, get_attributes, empty_list_if_none, empty_dict_if_none

TYPE_MAPPER: dict = {
    datetime: lambda v: v.isoformat(),
    dict: lambda v: {_k: safe_cast(_v or {}, dict, False) for _k, _v in v.items()},
    list: lambda v: [safe_cast(_v or {}, dict, False) for _v in v]
}


class Dictable(ABC):
    def __init_subclass__(cls, **kwargs):
        if cls not in TYPE_MAPPER:
            TYPE_MAPPER[cls] = dict

    def __iter__(self):
        for name, value in get_attributes(self):
            v_type = type(value)
            if v_type in TYPE_MAPPER:
                value = TYPE_MAPPER[v_type](value)
            yield name, value


class AbstractJsonIndexModelsDict(Dictable, ABC):
    def __init__(self, source=None):
        self.source = empty_dict_if_none(source)

    def __iter__(self):
        for k, v in self.source.items():
            yield k, dict(v)


class AbstractJsonIndexModelsList(Dictable, ABC):
    def __init__(self, source=None):
        self.source = empty_list_if_none(source)

    def __iter__(self):
        for v in self.source:
            yield dict(v)


class AbstractJsonIndexModel(Dictable, ABC):
    def __init__(self, **kwargs):
        self.updated_at = parse_iso_dt(kwargs.get('updated_at'))
        self.created_at = parse_iso_dt(kwargs.get('created_at'))
