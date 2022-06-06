from threading import Thread as _Thread


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


def run_in_separate_thread(target, args=None, kwargs=None, *thread_wrapper_args, **thread_wrapper_kwargs):
    wrapper = ThreadWrapper(
        target=target,
        args=args,
        kwargs=kwargs,
        daemon=True,
        *thread_wrapper_args,
        **thread_wrapper_kwargs
    )
    wrapper.thread.start()
    return wrapper

