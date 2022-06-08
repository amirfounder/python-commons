from heapq import heappush, heappop


class MinHeap:
    def __init__(self):
        self.heap = []

    def add(self, item):
        heappush(self.heap, item)

    def pop(self):
        if self.heap:
            return heappop(self.heap)

    def peek(self):
        if self.heap:
            return self.heap[-1]
