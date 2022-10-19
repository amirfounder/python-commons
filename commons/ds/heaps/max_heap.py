from .base import AbstractHeap
from heapq import heappop, heappush


class MaxHeap(AbstractHeap):
    def add(self, item):
        if isinstance(item, MaxHeapItem):
            item = (item.key, item.value)

        if isinstance(item, tuple):
            item = (-item[0], item[1])

        else:
            item = -item

        heappush(self._heap, item)

    def pop(self):
        if self._heap:
            return -heappop(self._heap)

    def peek(self):
        if self._heap:
            return -self._heap[-1]


class MaxHeapItem:
    def __init__(self, key, value):
        self.key = key
        self.value = value
