from commons.ds.multi_key_index import MultiKeyIndex


class MultiKeyIndexLRUCache:
    def __init__(
            self,
            primary_key: str,
            secondary_keys: list,
            max_object_count=100,
    ):
        self.max_object_count = max_object_count
        self.index = MultiKeyIndex(primary_key, secondary_keys)
        self.object_count = 0

    def _pop_lru(self):
        lru_key = next(iter(self.index.primary_index))
        return self.index.pop(lru_key)

    def _push_to_mru(self, obj):
        key = obj[self.index.primary_index_key]

        self.index.primary_index.pop(key)
        self.index.primary_index[key] = obj

    def set_max_object_count(self, max_object_count):
        self.max_object_count = max_object_count
        while self.object_count > self.max_object_count:
            self._pop_lru()

    def add(self, obj: dict):
        self.index.add(obj)
        self.object_count += 1

        while self.object_count > self.max_object_count:
            self._pop_lru()

    def query(self, query: dict):
        objs = self.index.query(query)
        for obj in objs:
            self._push_to_mru(obj)
        return objs

    def get_all(self, key, value):
        objs = self.index.get_all(key, value)
        for obj in objs:
            self._push_to_mru(obj)
        return objs

    def get_one(self, key, value, at_index=0):
        obj = self.index.get_one(key, value, at_index)
        self._push_to_mru(obj)
        return obj

    def get_first(self, key, value):
        obj = self.index.get_first(key, value)
        self._push_to_mru(obj)
        return obj
