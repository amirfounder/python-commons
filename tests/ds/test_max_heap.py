import random
import timeit

from python_lib.ds.heaps.max_heap import MaxHeap


def test_max_heap():
    heap = MaxHeap()

    res = []
    values = [random.randint(0, 1000) for _ in range(100)]

    for value in values:
        heap.add(value)

    while len(heap) > 0:
        res.append(heap.pop())

    assert res == sorted(values, reverse=True)
