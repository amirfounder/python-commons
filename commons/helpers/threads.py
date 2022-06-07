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


def run_in_separate_thread(target, *args, **kwargs):
    wrapper = ThreadWrapper(
        target=target,
        daemon=True,
        *args,
        **kwargs
    )
    wrapper.thread.start()
    return wrapper


def start_threads(threads: Iterable[_Thread | ThreadWrapper]):
    for thread in threads:
        if isinstance(thread, ThreadWrapper):
            thread = thread.thread
        thread.start()


def join_threads(threads: Iterable[_Thread | ThreadWrapper]):
    for thread in threads:
        if isinstance(thread, ThreadWrapper):
            thread = thread.thread
        thread.start()

