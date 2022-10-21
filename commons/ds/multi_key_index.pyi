from typing import Iterable, Dict, Set, List, Optional, Any


class MultiKeyIndex:
    """
    A data structure that supports querying your data by multiple keys. A primary key is required (often 'id') and
    secondary keys are optional. All operations run in O(1) time - arguably O(k) where k is the length of the
    secondary index keys list.
    """

    def __init__(self, primary_index_key: str, secondary_index_keys: Iterable[str]):
        """
        Time complexity: O(k) where k is the length of the secondary index keys list.
        :param primary_index_key: The primary key of the objects in the index. This is required.
        :param secondary_index_keys:
        """
        self.primary_index_key: str = ...
        self.secondary_index_keys: Set[str] = ...
        self.primary_index: dict[str | int, dict] = ...
        self.secondary_indices: Dict[str, Dict[str | int, Set[str]]] = ...

    def _remove_object_references_from_secondary_indices(self, obj: dict):
        """
        Time complexity: O(k) where k is the length of the secondary index keys list.
        :param obj:
        :return:
        """
        ...

    def _add_object_reference_to_secondary_indices(self, obj: dict):
        """
        Time complexity: O(k) where k is the length of the secondary index keys list.
        :param obj:
        :return:
        """
        ...

    def _validate_object(self, obj: dict):
        """
        Time complexity: O(k) where k is the length of the secondary index keys list.

        Validates that the object has all the keys required by the index.
        :param obj: The object to validate.
        :return: None
        """
        ...

    def add(self, obj: dict) -> dict:
        """
        Time complexity: O(k) where k is the length of the secondary index keys list.

        Adds an object to the index. If an object with the same primary key value already exists in the index, it will
        be removed and overwritten. This ensures that secondary indices are cleaned up and the order of the objects
        in the primary index is preserved.

        :param obj: The object to add to the index.

        :return: obj
        """
        ...

    def pop(self, primary_index_key_value, default=None) -> Optional[dict]:
        """
        Pops an object from the index by its primary key value. Then removes it from all secondary indices.
        :param primary_index_key_value: The value of the primary key of the object to remove.
        :param default: The default value to return if the object is not found.
        :return: None
        """
        ...

    def query(self, query: dict = None) -> List[dict]:
        """
        Queries the index by a dictionary of key-value pairs. The keys must be in the index. If the values are not in
        the associated index, an empty list will be returned. If the query contains an 'id' key, the value of that key
        will be used to query the primary index and return a list of length 1.
        :param query:
        :return:
        """
        ...

    def get_all(self, key, value) -> List[dict]:
        """
        Returns all objects in the index that have the given key-value pair in their secondary index.
        :param key: The key to query.
        :param value: The value to query.
        :return:
        """
        ...

    def get_one(self, key: str, value: any, at_index: int = 0) -> dict:
        """
        Returns the object at the given index in the list of objects that have the given key-value pair in their
        secondary index.
        :param key: The key to query.
        :param value: The value to query.
        :param at_index: The index of the object to return. Defaults to 0.
        :return:
        """
        ...

    def get_first(self, key, value) -> dict:
        """
        Returns the first object in the list of objects that have the given key-value pair in their secondary index.
        :param key: The key to query.
        :param value: The value to query.
        :return:
        """
        ...