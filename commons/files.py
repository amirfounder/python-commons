import json


def format_exception_caught_message(e: Exception):
    return f'Caught {type(e).__name__} Exception: {str(e)}'


def read(path, mode='r', encoding='utf-8', **kwargs):
    kwargs.update({
        'file': path,
        'mode': mode,
        'encoding': encoding
    })

    if mode.endswith('b'):
        kwargs.pop('encoding')

    with open(**kwargs) as f:
        return f.read()


def write(path, contents, mode='w', encoding='utf-8', **kwargs):
    kwargs.update({
        'file': path,
        'mode': mode,
        'encoding': encoding
    })

    if mode.endswith('b'):
        kwargs.pop('encoding')

    with open(**kwargs) as f:
        f.write(contents)


def safe_read(path, mode='r', encoding='utf-8', log_on_failure=True, log_fn=print, **kwargs):
    try:
        return read(path, mode, encoding, **kwargs)

    except Exception as e:
        if log_on_failure:
            msg = format_exception_caught_message(e)
            log_fn(msg)


def safe_write(path, contents, mode='w', encoding='utf-8', log_on_failure=True, log_fn=print, **kwargs):
    try:
        write(path, contents, mode, encoding, **kwargs)

    except Exception as e:
        if log_on_failure:
            msg = format_exception_caught_message(e)
            log_fn(msg)


def read_dict_from_json(path, default=None, **kwargs):
    if default is None:
        default = {}

    result = safe_read(path, **kwargs)

    if result is None:
        result = default
    else:
        result = json.loads(result)

    return result


def write_dict_as_json(path, dict_obj, indent=4, sort_keys=True, log_on_failure=True, log_fn=print):
    try:
        json_obj = json.dumps(dict_obj, indent=indent, sort_keys=sort_keys)
        safe_write(path, json_obj, log_on_failure=log_on_failure, log_fn=log_fn)

    except Exception as e:
        if log_on_failure:
            msg = format_exception_caught_message(e)
            log_fn(msg)
