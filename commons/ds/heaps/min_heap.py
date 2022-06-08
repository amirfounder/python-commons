from .base import AbstractHeap
from heapq import heappop, heappush


class MinHeap(AbstractHeap):
    def add(self, item):
        heappush(self._heap, item)

    def pop(self):
        if self._heap:
            return heappop(self._heap)

    def peek(self):
        if self._heap:
            return self._heap[-1]
