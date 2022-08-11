from abc import ABC, abstractmethod
from typing import Optional, List


class AbstractHeap(ABC):
    def __init__(self, items: Optional[List] = None):
        if items is None:
            items = []

        self._heap = []
        for item in items:
            self.add(item)

    def __len__(self):
        return len(self._heap)

    @abstractmethod
    def add(self, item):
        pass

    @abstractmethod
    def pop(self):
        pass

    @abstractmethod
    def peek(self):
        if self._heap:
            return self._heap[-1]
