from collections import defaultdict
from typing import List, Optional, Iterable, Generic, TypeVar


_T = TypeVar('_T')

class MultiKeyIndexObject(Generic[_T]):
    def __init__(self, obj: _T, context: dict = None):
        self.value = obj
        self.context = context or {}


class MultiKeyIndex:
    def __init__(self, primary_index_object_key: str, secondary_index_object_keys: Iterable[str] = None):
        self.primary_index_object_key = primary_index_object_key
        self.secondary_index_object_keys = set(secondary_index_object_keys or [])
        self.primary_index = {}
        self.secondary_indices = {key: defaultdict(set) for key in self.secondary_index_object_keys}

    def _remove_object_references_from_secondary_indices(self, obj: dict):
        for key in self.secondary_index_object_keys:
            value = obj[key]

            if key not in self.secondary_indices or value not in self.secondary_indices[key]:
                continue

            self.secondary_indices[key][value].remove(obj[self.primary_index_object_key])

            if not self.secondary_indices[key][value]:
                self.secondary_indices[key].pop(value)

    def _add_object_reference_to_secondary_indices(self, obj: dict):
        for key in self.secondary_index_object_keys:
            value = obj[key]

            if key not in self.secondary_indices:
                self.secondary_indices[key] = defaultdict(set)

            self.secondary_indices[key][value].add(obj[self.primary_index_object_key])

    def _validate_object(self, obj: dict):
        missing_keys = []
        for key in [self.primary_index_object_key, *self.secondary_index_object_keys]:
            if key not in obj:
                missing_keys.append(key)

        if missing_keys:
            raise KeyError(f'Object missing keys: {missing_keys}')

    def add(self, obj: MultiKeyIndexObject):
        self._validate_object(obj.value)
        primary_index_object_key_value = obj.value[self.primary_index_object_key]

        if self.primary_index.get(primary_index_object_key_value):
            self.pop(primary_index_object_key_value)

        self.primary_index[primary_index_object_key_value] = obj
        self._add_object_reference_to_secondary_indices(obj.value)

    def pop(self, primary_index_object_key_value) -> Optional[MultiKeyIndexObject]:
        if obj := self.primary_index.pop(primary_index_object_key_value, None):
            self._remove_object_references_from_secondary_indices(obj.value)
        return obj

    def query(self, query: dict = None) -> List[MultiKeyIndexObject]:
        if not query:
            return list(self.primary_index.values())

        if primary_index_object_key_value := query.pop(self.primary_index_object_key, None):
            return [self.primary_index.get(primary_index_object_key_value)]

        matched_ids_sets = []
        for key, value in query.items():
            if key not in self.secondary_index_object_keys:
                raise ValueError(f'Invalid key: {key}')

            matched_ids_set = self.secondary_indices[key].get(value)
            if not matched_ids_set:
                return []

            matched_ids_sets.append(matched_ids_set)

        matched_ids = set.intersection(*matched_ids_sets)
        if not matched_ids:
            return []

        return [self.primary_index[id_] for id_ in matched_ids]

    def get_all(self, key, value) -> List[dict]:
        return self.query({key: value})

    def get_first(self, key, value) -> dict:
        results = self.query({key: value})
        return results[0] if results else None
