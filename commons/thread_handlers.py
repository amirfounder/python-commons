from threading import Thread as _Thread


class Thread:
    def __init__(self, target, args=None, kwargs=None, daemon=True, *thread_args, **thread_kwargs):
        self._result = [None]
        self.target = self.build_threaded_fn(target)
        self.thread = _Thread(
            target=self.target,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
            *thread_args,
            **thread_kwargs
        )

    def build_threaded_fn(self, func):
        def inner(*args, **kwargs):
            self._result[0] = func(*args, **kwargs)
        return inner

    @property
    def result(self):
        return self._result[0]
