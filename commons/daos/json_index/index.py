from abc import ABC

from commons.helpers.files import (
    safe_write_obj_as_json_to_file,
    safe_read_json_as_obj_from_file,
    ensure_path_exists
)


class AbstractJsonIndex(ABC):
    def __init__(self, source_path, flush_after_put=False, load=True):
        self.source_path = source_path
        self.flush_after_put = flush_after_put
        self.source = None

        ensure_path_exists(self.source_path)
        if load:
            self.load()

    def __len__(self):
        return len(self.source)

    def __iter__(self):
        return iter(self.source)

    def __contains__(self, o):
        return o in self.source

    def put(self, key, value, **kwargs):
        flush = kwargs['flush'] if 'flush' in kwargs else self.flush_after_put
        self.source[key] = value
        if flush:
            self.flush()

    def get(self, key, default=None):
        return self.source.get(key, default)

    def all(self):
        for k, v in self.source:
            yield k, v

    def load(self):
        self.source = safe_read_json_as_obj_from_file(self.source_path, {})

    def flush(self):
        safe_write_obj_as_json_to_file(self.source_path, self.source)
