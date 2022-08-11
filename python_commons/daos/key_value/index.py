from typing import Mapping, Any

import orjson

from python_commons.helpers import safe_read_json_as_obj_from_file, safe_write_obj_as_json_to_file


class KeyValueIndex(Mapping[str, Any]):
    def __init__(self, model, path, configs):
        self.model = model
        self.path = path
        self.configs = configs
        self.source = {}
        self.load()

    def __iter__(self):
        return self.source.__iter__()

    def __len__(self) -> int:
        return self.source.__len__()

    def __contains__(self, item):
        return self.source.__contains__(item)

    def __getitem__(self, item):
        return self.source.__getitem__(item)

    def __setitem__(self, key, value):
        self.source.__setitem__(key, value)
        if self.configs.get('flush_after_set', False):
            self.flush()

    def get(self, key, default=None):
        return self.source.get(key, default)

    def keys(self):
        return self.source.keys()

    def values(self):
        return self.source.values()

    def items(self):
        return self.source.items()

    def pop(self, key, default=None):
        return self.source.pop(key, default)

    def load(self):
        self.source = safe_read_json_as_obj_from_file(self.path, {})
        for k, v in self.source.items():
            self.source[k] = self.model.parse_obj(v)

    def flush(self):
        obj = {}
        for k, v in self.source.items():
            obj[k] = orjson.loads(v.json())
        safe_write_obj_as_json_to_file(self.path, obj)
