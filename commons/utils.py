import uuid
from typing import Any, Type


def gen_uuid(cast_type: Type = str):
    id_ = uuid.uuid4()
    return safe_cast(id_, cast_type, id_)


def swap(arr, idx1, idx2):
    arr[idx1], arr[idx2] = arr[idx2], arr[idx1]


def merge_lists(*args):
    result = []
    for arg in args:
        if isinstance(arg, list):
            result.extend(arg)
    return result


def safe_cast(value, type_, default_return: Any = None, return_exception: bool = False):
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

def unique_type_set_from_list(list_: list):
    return set([type(o) for o in list_])

def exhaust(iterator, should_return=False):
    if should_return:
        return [x for x in iterator]
    else:
        for _ in iterator:
            pass
