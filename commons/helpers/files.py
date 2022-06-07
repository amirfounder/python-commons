import json
from os import makedirs
from os.path import exists


def format_exception_caught_message(e: Exception):
    return f'Caught {type(e).__name__} Exception: {str(e)}'


def create_file(path):
    open(path, 'x').close()


def ensure_path_exists(path, is_file=True):
    if exists(path):
        return

    folders = path.split('/')
    filepath = None
    
    if is_file:
        filepath = folders.pop()
    
    dir_path = '/'.join(folders)

    if not exists(dir_path):
        makedirs(dir_path)
    
    if is_file:
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
        ensure_path_exists(path)
        return read_from_file(path, mode, encoding, **kwargs)

    except Exception as e:
        if log_on_exception:
            msg = format_exception_caught_message(e)
            log_fn(msg)


def safe_write_to_file(path, contents, mode='w', encoding='utf-8', log_on_exception=True, log_fn=print, **kwargs):
    try:
        ensure_path_exists(path)
        write_to_file(path, contents, mode, encoding, **kwargs)

    except Exception as e:
        if log_on_exception:
            msg = format_exception_caught_message(e)
            log_fn(msg)


def safe_read_json_as_obj_from_file(path, default=None, log_on_exception=True, log_fn=print, **kwargs):
    result = safe_read_from_file(path, **kwargs)

    try:
        result = json.loads(result)
    except Exception as e:
        result = default
        if log_on_exception:
            msg = format_exception_caught_message(e)
            log_fn(msg)

    return result


def safe_write_obj_as_json_to_file(path, dict_obj, indent=4, sort_keys=True, log_on_exception=True, log_fn=print):
    try:
        json_obj = json.dumps(dict_obj, indent=indent, sort_keys=sort_keys)
        safe_write_to_file(path, json_obj, log_on_exception=log_on_exception, log_fn=log_fn)

    except Exception as e:
        if log_on_exception:
            msg = format_exception_caught_message(e)
            log_fn(msg)
