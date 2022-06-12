from __future__ import annotations

from commons.helpers import safe_read_json_as_obj_from_file, safe_write_to_file


class JsonIndexBuilder:
    def __init__(self):
        self.cls = JsonIndex
        self.cls_kwargs = {}

    def set_model(self, model):
        self.cls_kwargs['model'] = model
        return self

    def set_path(self, path):
        self.cls_kwargs['path'] = path
        return self

    def set_configs(self, configs):
        self.cls_kwargs['configs'] = configs
        return self

    def build(self):
        return self.cls(**self.cls_kwargs)


class JsonIndex:
    def __init__(self, model, path, configs):
        self.model = model
        self.path = path
        self.configs = configs
        self.source = {}
        self.load()

    def __contains__(self, item):
        return item in self.source

    def __getitem__(self, item):
        return self.source[item]

    def __setitem__(self, key, value):
        self.source[key] = value
        if self.configs.get('flush_after_set', False):
            self.flush()

    def get(self, key, default=None):
        return self.source.get(key, default)

    def load(self):
        self.source = safe_read_json_as_obj_from_file(self.path, {})
        for k, v in self.source.items():
            self.source[k] = self.model.parse_obj(v)

    def flush(self):
        obj = {}
        for k, v in self.source.items():
            obj[k] = v.json()

        json_stack = ["{"]
        for i, (k, v) in enumerate(obj.items()):
            json_stack.append(f'"{k}": {v}')
            if i < len(obj) - 1:
                json_stack.append(',')
        json_stack.append("}")
        json_obj = ''.join(json_stack)

        safe_write_to_file(self.path, json_obj)
