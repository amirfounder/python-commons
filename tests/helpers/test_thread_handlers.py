import time
from commons.helpers.threads import ThreadWrapper


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
