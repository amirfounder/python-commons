from commons.ds.multi_key_index import MultiKeyIndex


class MultiKeyIndexLRUCache:
    def __init__(
            self,
            primary_index_key: str,
            secondary_index_keys: list,
            max_object_count=100,
    ):
        self.max_object_count = max_object_count
        self.object_count = 0
        self.index = MultiKeyIndex(
            primary_index_key,
            secondary_index_keys
        )

    def _push_to_top(self, obj):
        self.index.shift_to_end(obj[self.index.primary_index_key])

    def add(self, obj: dict):
        self.index.add(obj)
        self.object_count += 1

        while self.object_count > self.max_object_count:
            self.index.popitem()

    def query(self, query: dict):
        objs = self.index.query(query)
        for obj in objs:
            self._push_to_top(obj)
        return objs

    def get_all(self, key, value):
        objs = self.index.get_all(key, value)
        for obj in objs:
            self._push_to_top(obj)
        return objs

    def get_one(self, key, value, at_index=0):
        obj = self.index.get_one(key, value, at_index)
        self._push_to_top(obj)
        return obj

    def get_first(self, key, value):
        obj = self.index.get_first_or_none(key, value)
        self._push_to_top(obj)
        return obj
