import json


def safe_read(path, mode='r', encoding='utf-8', log_fn=print):
    kwargs = {
        'file': path,
        'mode': mode,
        'encoding': encoding
    }

    if mode.endswith('b'):
        kwargs.pop('encoding')

    try:
        with open(**kwargs) as f:
            return f.read()

    except Exception as e:
        log_fn(f'Caught {type(e).__name__} Exception: {str(e)}')


def read_json(path, default=None):
    if default is None:
        default = {}

    result = safe_read(path)

    if result is None:
        result = default
    else:
        result = json.loads(result)

    return result
