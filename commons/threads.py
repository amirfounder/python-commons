import threading
import time
from random import randint
from threading import Thread as _Thread
from typing import Iterable


class ThreadWrapper:
    def __init__(self, target, *args, **kwargs):
        self.result = None
        self._target = self._build_target_fn(target)
        self.thread = _Thread(
            target=self._target,
            *args,
            **kwargs
        )

    def _build_target_fn(self, func):
        def inner(*args, **kwargs):
            self.result = func(*args, **kwargs)
        return inner


def active_count_by_name_prefix(prefix: str):
    return len([t for t in threading.enumerate() if t.name.startswith(prefix)])


def run_in_separate_thread(target, *args, **kwargs):
    if 'daemon' not in kwargs:
        kwargs['daemon'] = True

    wrapper = ThreadWrapper(
        target=target,
        *args,
        **kwargs
    )
    wrapper.thread.start()
    return wrapper

def start_threads(threads: Iterable[_Thread | ThreadWrapper], max_threads: int = 10, name_prefix: str = ''):
    name_prefix += f'{randint(0, 1000000)}_'
    name_suffix = 1

    for thread in threads:
        while active_count_by_name_prefix(name_prefix) >= max_threads:
            time.sleep(1)

        if isinstance(thread, ThreadWrapper):
            thread = thread.thread

        thread.name = f'{name_prefix}{name_suffix}'
        name_suffix += 1
        thread.start()


def join_threads(threads: Iterable[_Thread | ThreadWrapper]):
    for thread in threads:
        if isinstance(thread, ThreadWrapper):
            thread = thread.thread
        thread.join()

