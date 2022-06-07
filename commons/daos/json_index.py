from abc import ABC

from commons.helpers.files import (
    safe_write_obj_as_json_to_file,
    safe_read_json_as_obj_from_file,
    ensure_path_exists
)


class AbstractJsonIndex(ABC):
    def __init__(self, path, flush_after_put=False, load=True):
        self.path = path
        self.flush_after_put = flush_after_put
        self.source = None

        ensure_path_exists(self.path)
        if load:
            self.load()

    def __len__(self):
        return self.source.__len__()

    def __iter__(self):
        return self.source.__iter__()

    def __contains__(self, o):
        return self.source.__contains__(o)

    def put(self, key, value, **kwargs):
        flush = kwargs['flush'] if 'flush' in kwargs else self.flush_after_put
        self.source[key] = value
        if flush:
            self.flush()

    def get(self, key, default=None):
        return self.source.get(key, default)

    def load(self):
        self.source = safe_read_json_as_obj_from_file(self.path, {})

    def flush(self):
        safe_write_obj_as_json_to_file(self.path, self.source)
