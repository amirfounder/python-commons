import random
import timeit

from commons.ds.heaps.max_heap import MaxHeap


def test_max_heap():
    heap = MaxHeap()

    res = []
    values = [random.randint(0, 1000) for _ in range(100)]

    for value in [random.randint(0, 1000) for _ in range(100)]:
        heap.add(value)

    while len(heap) > 0:
        res.append(heap.pop())

    assert res == sorted(values, reverse=True)


def test_max_heap_sort_vs_native():
    heap = MaxHeap()
    values = [random.randint(0, 10000) for _ in range(10000)]

    def sort_using_heap():
        res = []
        for v in values:
            heap.add(v)
        while len(heap) > 0:
            res.append(heap.pop())
        return res

    def sort_using_native_fn():
        return sorted(values, reverse=True)

    heap_time = timeit.Timer(sort_using_heap).timeit(100)
    native_time = timeit.Timer(sort_using_native_fn).timeit(100)

    print('')
    print('Native Time: ', native_time)
    print('Heap Time: ', heap_time)
