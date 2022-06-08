from heapq import heappop, heappush


class MaxHeap:
    def __init__(self):
        self.heap = []

    def __len__(self):
        return len(self.heap)

    def add(self, item):
        heappush(self.heap, -item)

    def pop(self):
        if self.heap:
            return -heappop(self.heap)

    def peek(self):
        if self.heap:
            return -self.heap[-1]
