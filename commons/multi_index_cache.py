from collections import defaultdict
from typing import List


"""
Example Cache

host_cache: dict[str, MultiKeyIndex] = {
    'localhost:3000': {
        'model_class': ...,
        'primary_index_key': 'id',
        'secondary_index_keys': ['name', 'age'],
        '_cached': {
            1: {
                'id': 1,
                'name': 'John',
                'age': 18,
                'ssn': '123-45-6789'
            },
            2: {
                'id': 2,
                'name': 'John',
                'age': 19,
                'ssn': '234-56-7890'
            },
            3: {
                'id': 3,
                'name': 'Jane',
                'age': 20,
                'ssn': '345-67-8901'
            }
        },
        'indices: {
            'name': {
                'John': [1, 2],
                'Jane': [3]
            },
            'age': {
                18: [1],
                19: [2],
                20: [3]
            },
            'ssn': {
                '123-45-6789': [1],
                '234-56-7890': [2],
                '345-67-8901': [3]
            }
        }
    }
}

HOST = 'localhost:3000'

cache = host_cache[HOST]
cache.get(name='John')
cache.get({
    'age': '18'
})
cache.getFirst({
    'name': 'John',
    'age': '18'
})
"""


class MultiKeyIndex:
    def __init__(self, primary_index_key: str, secondary_index_keys: List[str]):
        self.primary_index_key = primary_index_key
        self.secondary_index_keys = set(secondary_index_keys)
        self.index_keys = {primary_index_key, *secondary_index_keys}
        self.data = {}

        self.load_indices()

    def load_indices(self):
        self.data[self.primary_index_key] = {}
        for secondary_index_key in self.secondary_index_keys:
            self.data[secondary_index_key] = defaultdict(set)

    def validate_object(self, obj: dict):
        missing_keys = []
        for key in self.index_keys:
            if key not in obj:
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f'Object missing keys: {missing_keys}')

    def add(self, obj: dict):
        self.validate_object(obj)
        primary_index_key_value = obj[self.primary_index_key]

        if self.data[self.primary_index_key].get(primary_index_key_value):
            self.remove(primary_index_key_value)

        self.data[self.primary_index_key][primary_index_key_value] = obj

        for key in self.secondary_index_keys:
            value = obj[key]
            self.data[key][value].add(obj[self.primary_index_key])

    def remove(self, primary_index_key_value):
        obj = self.data[self.primary_index_key].pop(primary_index_key_value)
        for key in self.secondary_index_keys:
            value = obj[key]
            self.data[key][value].remove(primary_index_key_value)

            if not self.data[key][value]:
                self.data[key].pop(value)

    def query(self, query: dict) -> List[dict]:
        id_ = query.pop('id', None)
        if id_:
            return [self.data[self.primary_index_key].get(id_)]

        matched_ids_sets = []
        for key, value in query.items():
            if key not in self.secondary_index_keys:
                raise ValueError(f'Invalid key: {key}')

            matched_ids_sets.append(self.data[key].get(value, None) or set())

        while len(matched_ids_sets) > 1:
            matched_ids_sets.append(matched_ids_sets.pop() & matched_ids_sets.pop())

        return [self.data[self.primary_index_key][id_] for id_ in matched_ids_sets[0]]

    def get_all(self, key, value) -> List[dict]:
        return self.query({key: value})

    def get_one(self, key: str, value: any, at_index: int = 0) -> dict:
        results = self.get_all(key, value)
        return results[at_index]

    def get_first_or_none(self, key, value) -> dict:
        results = self.get_all(key, value)
        return results[0] if results else None