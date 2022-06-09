def merge_lists(*args):
    result = []
    for arg in args:
        if isinstance(arg, list):
            result.extend(arg)
    return result


def safe_cast(value, type_, return_exception: bool = True):
    try:
        type_(value)
    except Exception as e:
        if return_exception:
            return e


def get_attributes(cls, include_private=False, include_dunder=False, include_callables=False):
    for name in dir(cls):
        if not include_dunder and name.startswith('__'):
            continue
        if not include_private and name.startswith('_'):
            continue
        attr = getattr(cls, name)
        if not include_callables and callable(attr):
            continue
        yield name, attr


def empty_list_if_none(o):
    if o is None:
        return []
    return o


def empty_dict_if_none(o):
    if o is None:
        return {}
    return o
