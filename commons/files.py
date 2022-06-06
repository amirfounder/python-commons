import json


def format_exception_caught_message(e: Exception):
    return f'Caught {type(e).__name__} Exception: {str(e)}'


def safe_read(path, mode='r', encoding='utf-8', log_on_failure=True, log_fn=print, **kwargs):
    kwargs.update({
        'file': path,
        'mode': mode,
        'encoding': encoding
    })

    if mode.endswith('b'):
        kwargs.pop('encoding')

    try:
        with open(**kwargs) as f:
            return f.read()

    except Exception as e:
        if log_on_failure:
            msg = format_exception_caught_message(e)
            log_fn(msg)


def safe_write(path, contents, mode='w', encoding='utf-8', log_on_failure=True, log_fn=print, **kwargs):
    kwargs.update({
        'file': path,
        'mode': mode,
        'encoding': encoding
    })

    if mode.endswith('b'):
        kwargs.pop('encoding')

    try:
        with open(**kwargs) as f:
            f.write(contents)

    except Exception as e:
        if log_on_failure:
            msg = format_exception_caught_message(e)
            log_fn(msg)


def read_json(path, default=None, **kwargs):
    if default is None:
        default = {}

    result = safe_read(path, **kwargs)

    if result is None:
        result = default
    else:
        result = json.loads(result)

    return result


def write_dict_as_json(path, dict_obj, log_on_failure=True, log_fn=print, *args, **kwargs):
    if 'indent' not in kwargs:
        kwargs['indent'] = 4
    if 'sort_keys' not in kwargs:
        kwargs['sort_keys'] = True

    try:
        json_obj = json.dumps(dict_obj, *args, **kwargs)
        safe_write(path, json_obj, log_on_failure=log_on_failure, log_fn=log_fn)

    except Exception as e:
        if log_on_failure:
            msg = format_exception_caught_message(e)
            log_fn(msg)
