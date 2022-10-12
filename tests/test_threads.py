import threading
import time
from unittest import TestCase

from commons.threads import ThreadWrapper


def test():

    def target():
        print('Starting test function')
        time.sleep(1)
        return 'Hello'

    wrapper = ThreadWrapper(target=target)
    wrapper.thread.start()

    r = wrapper.result
    assert r is None

    time.sleep(2)

    r = wrapper.result
    assert r == 'Hello'


class TestThreadLocal(TestCase):
    def test(self):
        local = threading.local()

        def func(val):
            local.value = val
            print(local.value)
            time.sleep(1)
            print(local.value)

        t1 = threading.Thread(target=func, args=(1,))
        t2 = threading.Thread(target=func, args=(2,))

        t1.start()
        time.sleep(.5)
        t2.start()

        time.sleep(1.5)
