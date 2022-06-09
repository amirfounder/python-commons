from abc import ABC
from datetime import datetime
from commons.util import safe_cast


class Dictable(ABC):
    def __init__(self):
        self._type_map = {
            datetime: lambda v: v.isoformat(),
            AbstractJsonIndexModel: lambda v: dict(v),
            dict: lambda v: {_k: safe_cast(_v or {}, dict, False) for _k, _v in v.items()},
            list: lambda v: [safe_cast(_v or {}, dict, False) for _v in v]
        }

    def __iter__(self):
        items = []
        for name in dir(self):
            attr = getattr(self, name)
            if not name.startswith('_') and not callable(name):
                items.append((name, attr))

        for name, value in items:
            v_type = type(value)
            if v_type is not str:
                if v_type in self._type_map:
                    value = self._type_map[v_type](value)
                else:
                    value = str(value)
            yield name, value

    def _register_type_cast_fn(self, type_, cast_fn):
        self._type_map[type_] = cast_fn


class AbstractJsonIndexModel(Dictable, ABC):
    pass
