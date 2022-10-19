from collections import defaultdict
from typing import List


class OrderedKeyIndex:
    def __init__(self):
        self._keys = []
        self._data = dict()
        self.minheap = []
        self.maxheap = []

    def get(self, key: str):
        """
        Returns the value at the specified key or None if the key does not exist. Runs O(1) time.
        """
        return self._data.get(key)

    def get_largest(self):
        """
        Returns the value a the largest key
        :return:
        """
        pass

    def get_smallest(self):
        """
        Returns the value a the smallest key
        """
        pass

    def set(self, key, value):
        pass


class MultiKeyIndex:
    """
    A data structure that supports querying your data by multiple keys. A primary key is required (often 'id') and
    secondary keys are optional. All operations run in O(1) time - arguably O(k) where k is the length of the
    secondary index keys list.
    """

    def __init__(self, primary_index_key: str, secondary_index_keys: List[str] = None):
        """
        :param primary_index_key: The primary key of the objects in the index. This is required.
        :param secondary_index_keys:
        """
        self.primary_index_key = primary_index_key
        self.secondary_index_keys = set(secondary_index_keys or [])
        self.index_keys = {self.primary_index_key, *self.secondary_index_keys}
        self.data = {
            self.primary_index_key: {},
            **{key: defaultdict(set) for key in self.secondary_index_keys}
        }

    def validate_object(self, obj: dict):
        """
        Validates that the object has all the keys required by the index.
        :param obj: The object to validate.
        :return: None
        """
        missing_keys = []
        for key in self.index_keys:
            if key not in obj:
                missing_keys.append(key)

        if missing_keys:
            raise ValueError(f'Object missing keys: {missing_keys}')

    def add(self, obj: dict):
        """
        Adds an object to the index. If an object with the same primary key value already exists in the index, it will
        be removed and overwritten.
        :param obj: The object to add to the index.
        :return:
        """
        self.validate_object(obj)
        primary_index_key_value = obj[self.primary_index_key]

        if self.data[self.primary_index_key].get(primary_index_key_value):
            self.remove(primary_index_key_value)

        self.data[self.primary_index_key][primary_index_key_value] = obj

        for key in self.secondary_index_keys:
            value = obj[key]
            self.data[key][value].add(obj[self.primary_index_key])

    def remove(self, primary_index_key_value):
        """
        Removes an object from the index by its primary key value. Then removes it from all secondary indexes.
        :param primary_index_key_value: The value of the primary key of the object to remove.
        :return: None
        """
        obj = self.data[self.primary_index_key].pop(primary_index_key_value)
        for key in self.secondary_index_keys:
            value = obj[key]
            self.data[key][value].remove(primary_index_key_value)

            if not self.data[key][value]:
                self.data[key].pop(value)

    def query(self, query: dict) -> List[dict]:
        """
        Queries the index by a dictionary of key-value pairs. The keys must be in the index. If the values are not in
        the associated index, an empty list will be returned. If the query contains an 'id' key, the value of that key
        will be used to query the primary index and return a list of length 1.
        :param query:
        :return:
        """
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
        """
        Returns all objects in the index that have the given key-value pair in their secondary index.
        :param key: The key to query.
        :param value: The value to query.
        :return:
        """
        return self.query({key: value})

    def get_one(self, key: str, value: any, at_index: int = 0) -> dict:
        """
        Returns the object at the given index in the list of objects that have the given key-value pair in their
        secondary index.
        :param key: The key to query.
        :param value: The value to query.
        :param at_index: The index of the object to return. Defaults to 0.
        :return:
        """
        results = self.get_all(key, value)
        return results[at_index]

    def get_first_or_none(self, key, value) -> dict:
        """
        Returns the first object in the list of objects that have the given key-value pair in their secondary index.
        :param key: The key to query.
        :param value: The value to query.
        :return:
        """
        results = self.get_all(key, value)
        return results[0] if results else None
