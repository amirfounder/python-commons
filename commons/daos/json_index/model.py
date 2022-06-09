from abc import ABC
from datetime import datetime
from typing import Any, Callable

from commons.util import safe_cast


class Dictable(ABC):
    _type_map: dict[Any, Callable] = {
        datetime: lambda v: v.isoformat(),
        dict: lambda v: {_k: safe_cast(_v or {}, dict, False) for _k, _v in v.items()},
        list: lambda v: [safe_cast(_v or {}, dict, False) for _v in v]
    }

    def __init_subclass__(cls, **kwargs):
        if cls not in cls._type_map:
            cls._type_map[cls] = dict

    def __iter__(self):
        items = []
        for name in dir(self):
            attr = getattr(self, name)
            if not name.startswith('_') and not callable(name):
                items.append((name, attr))

        for name, value in items:
            v_type = type(value)
            if v_type not in [str, int, bool, list, dict]:
                if v_type in self._type_map:
                    value = self._type_map[v_type](value)
                else:
                    value = str(value)
            yield name, value


class AbstractJsonIndexModel(Dictable, ABC):
    pass
