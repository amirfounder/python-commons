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
