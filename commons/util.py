from typing import Any


def merge_lists(*args):
    result = []
    for arg in args:
        if isinstance(arg, list):
            result.extend(arg)
    return result


def safe_cast(value, type_, return_exception: bool = False, default_return: Any = None):
    try:
        return type_(value)
    except Exception as e:
        if return_exception:
            return e
        if default_return:
            return default_return


def get_attributes(
        cls,
        include_private=False,
        include_dunder=False,
        include_callables=False,
        include_base=True
):
    for name in dir(cls):
        if not include_dunder and name.startswith('__'):
            continue
        if not include_private and name.startswith('_'):
            continue
        if not include_base:
            pass
        attr = getattr(cls, name)
        if not include_callables and callable(attr):
            continue
        yield name, attr


def empty_list_if_none(o):
    return this_if_none(o, [])


def empty_dict_if_none(o):
    return this_if_none(o, {})


def this_if_none(o, this, else_=None):
    if else_ is None:
        else_ = o
    return this if o is None else else_


