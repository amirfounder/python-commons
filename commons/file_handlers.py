import json
from os import makedirs
from os.path import exists


def format_exception_caught_message(e: Exception):
    return f'Caught {type(e).__name__} Exception: {str(e)}'


def create_file(path):
    open(path, 'x').close()


def ensure_filepath_exists(path):
    if exists(path):
        return

    folders = path.split('/')
    filepath = folders.pop()
    dir_path = '/'.join(folders)

    makedirs(dir_path)

    path = '/'.join([dir_path, filepath])

    create_file(path)


def read_from_file(path, mode='r', encoding='utf-8', **kwargs):
    kwargs.update({
        'file': path,
        'mode': mode,
        'encoding': encoding
    })

    if mode.endswith('b'):
        kwargs.pop('encoding')

    with open(**kwargs) as f:
        return f.read()


def write_to_file(path, contents, mode='w', encoding='utf-8', **kwargs):
    kwargs.update({
        'file': path,
        'mode': mode,
        'encoding': encoding
    })

    if mode.endswith('b'):
        kwargs.pop('encoding')

    with open(**kwargs) as f:
        f.write(contents)


def safe_read_from_file(path, mode='r', encoding='utf-8', log_on_exception=True, log_fn=print, **kwargs):
    try:
        ensure_filepath_exists(path)
        return read_from_file(path, mode, encoding, **kwargs)

    except Exception as e:
        if log_on_exception:
            msg = format_exception_caught_message(e)
            log_fn(msg)


def safe_write_to_file(path, contents, mode='w', encoding='utf-8', log_on_exception=True, log_fn=print, **kwargs):
    try:
        ensure_filepath_exists(path)
        write_to_file(path, contents, mode, encoding, **kwargs)

    except Exception as e:
        if log_on_exception:
            msg = format_exception_caught_message(e)
            log_fn(msg)


def read_json_as_dict_from_file(path, default=None, **kwargs):
    result = safe_read_from_file(path, **kwargs)

    if result is None:
        result = default
    else:
        result = json.loads(result)

    return result


def write_dict_as_json_to_file(path, dict_obj, indent=4, sort_keys=True, log_on_exception=True, log_fn=print):
    try:
        json_obj = json.dumps(dict_obj, indent=indent, sort_keys=sort_keys)
        safe_write_to_file(path, json_obj, log_on_exception=log_on_exception, log_fn=log_fn)

    except Exception as e:
        if log_on_exception:
            msg = format_exception_caught_message(e)
            log_fn(msg)
