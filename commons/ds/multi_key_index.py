from collections import defaultdict
from typing import List, Optional, Iterable

from commons.utils import pop_first, pop_last


class MultiKeyIndex:

    def __init__(self, primary_index_key: str, secondary_index_keys: Iterable[str] = None):
        self.primary_index_key = primary_index_key
        self.secondary_index_keys = set(secondary_index_keys or [])
        self.primary_and_secondary_index_keys = {self.primary_index_key, *self.secondary_index_keys}
        self.primary_index = {}
        self.secondary_indices = {key: defaultdict(set) for key in self.secondary_index_keys}

    def remove_object_references_from_secondary_indices(self, obj: dict):
        for key in self.secondary_index_keys:
            value = obj[key]
            self.secondary_indices[key][value].remove(obj[self.primary_index_key])

            if not self.secondary_indices[key][value]:
                self.secondary_indices[key].pop(value)

    def add_object_reference_to_secondary_indices(self, obj: dict):
        for key in self.secondary_index_keys:
            value = obj[key]
            self.secondary_indices[key][value].add(obj[self.primary_index_key])

    def validate_object(self, obj: dict):
        missing_keys = []
        for key in self.primary_and_secondary_index_keys:
            if key not in obj:
                missing_keys.append(key)

        if missing_keys:
            raise KeyError(f'Object missing keys: {missing_keys}')

    def add(self, obj: dict):
        self.validate_object(obj)
        primary_index_key_value = obj[self.primary_index_key]

        if self.primary_index.get(primary_index_key_value):
            self.pop(primary_index_key_value)

        self.primary_index[primary_index_key_value] = obj
        self.add_object_reference_to_secondary_indices(obj)

    def popitem(self, first=False) -> dict:
        pop_fn = pop_first if first else pop_last
        obj = pop_fn(self.primary_index)
        self.remove_object_references_from_secondary_indices(obj)
        return obj

    def shift_to_end(self, primary_index_key_value):
        obj = self.primary_index.pop(primary_index_key_value)
        self.primary_index[primary_index_key_value] = obj

    def pop(self, primary_index_key_value) -> Optional[dict]:
        obj = self.primary_index.pop(primary_index_key_value, None)

        if obj:
            self.remove_object_references_from_secondary_indices(obj)

        return obj

    def query(self, query: dict = None) -> List[dict]:
        if not query:
            return list(self.primary_index.values())

        if id_ := query.pop('id', None):
            return [self.primary_index.get(id_)]

        matched_ids_sets = []
        for key, value in query.items():
            if key not in self.secondary_index_keys:
                raise ValueError(f'Invalid key: {key}')

            matched_ids_set = self.secondary_indices[key].get(value)
            if not matched_ids_set:
                return []

            matched_ids_sets.append(matched_ids_set)

        while len(matched_ids_sets) > 1:
            matched_ids_sets.append(matched_ids_sets.pop() & matched_ids_sets.pop())

        results = []

        for id_ in matched_ids_sets[0]:
            results.append(self.primary_index[id_])

        return results

    def get_all(self, key, value) -> List[dict]:
        return self.query({key: value})

    def get_one(self, key: str, value: any, at_index: int = 0) -> dict:
        results = self.get_all(key, value)
        return results[at_index]

    def get_first_or_none(self, key, value) -> dict:
        results = self.get_all(key, value)
        return results[0] if results else None
