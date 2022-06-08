from multipledispatch import dispatch
from mss import mss


def _screenshot(sct, monitor: dict[str, int]):
    return sct.grab(monitor)


@dispatch(dict[str, int])
def screenshot(monitor: dict[str, int]):
    valid_keys = ['top', 'left', 'width', 'height']

    if len(monitor) != 4:
        raise Exception('Invalid monitor')

    for k in valid_keys:
        if k not in monitor:
            raise Exception('Invalid monitor')

    with mss() as sct:
        _screenshot(sct, monitor)


@dispatch(int)
def screenshot(monitor_idx: int):
    with mss() as sct:
        monitor = sct.monitors[monitor_idx]
        return _screenshot(sct, monitor)


@dispatch((tuple[int, int, int, int], list[int]))
def screenshot(rect: tuple[int, int, int, int] | list[int]):
    y, x, w, h = rect
    monitor = {'top': y, 'left': x, 'width': w, 'height': h}
    with mss() as sct:
        return _screenshot(sct, monitor)
