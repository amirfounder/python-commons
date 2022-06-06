from threading import Thread as _Thread


class ThreadWrapper:
    def __init__(self, target, daemon=True, *args, **kwargs):
        self.result = None
        self._target = self._build_target_fn(target)
        self.thread = _Thread(
            target=self._target,
            daemon=daemon,
            *args,
            **kwargs
        )

    def _build_target_fn(self, func):
        def inner(*args, **kwargs):
            self.result = func(*args, **kwargs)
        return inner
