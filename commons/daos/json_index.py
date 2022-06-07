from abc import ABC

from commons.helpers.files import (
    safe_write_obj_as_json_to_file,
    safe_read_json_as_obj_from_file,
    ensure_path_exists
)


class AbstractJsonIndex(ABC):
    def __init__(self, path, index={}, flush_after_put=False, load=True):
        self.path = path
        self.index = index
        self.flush_after_put = flush_after_put

        ensure_path_exists(self.path)
        if load:
            self.load()

    def __len__(self):
        return self.index.__len__()

    def __iter__(self):
        return self.index.__iter__()

    def __contains__(self, o):
        return self.index.__contains__(o)

    def put(self, key, value, **kwargs):
        flush = kwargs['flush'] if 'flush' in kwargs else self.flush_after_put
        self.index[key] = value
        if flush:
            self.flush()

    def load(self):
        self.index = safe_read_json_as_obj_from_file(self.path, {})

    def flush(self):
        safe_write_obj_as_json_to_file(self.path, self.index)
