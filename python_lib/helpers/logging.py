import os
from threading import current_thread
from typing import Optional

import multipledispatch

from python_lib.helpers.files import safe_write_to_file
from python_lib.helpers.datetime import now
from python_lib.helpers.env import get_working_env


PATH = None


def configure_logging_path(path):
    global PATH
    PATH = path


def _log(message, level: str = 'info'):
    message = {
        'timestamp': now().isoformat().ljust(39, '.') + ' ',
        'env': 'ENV: ' + str(get_working_env()).upper().ljust(9, '.') + ' ',
        'pid': 'PID: ' + str(os.getpid()).ljust(14, '.') + ' ',
        'thread': 'THREAD: ' + current_thread().name.ljust(44, '.') + ' ',
        'level': 'LEVEL: ' + level.upper().ljust(14, '.') + ' ',
        'message': message
    }

    message = ''.join(message.values())

    print(message)

    if PATH is not None:
        safe_write_to_file(PATH, message + '\n', mode='a')


def log_success(message):
    _log(message, 'success')


def log_info(message):
    _log(message, 'info')


@multipledispatch.dispatch(Exception)
def log_error(exception: Exception):
    message = f'Caught {type(exception).__name__} Exception: {str(exception)}'
    log_error(message)


@multipledispatch.dispatch(str)
def log_error(message: str):
    _log(message, 'error')


def log_warning(message):
    _log(message, 'warning')
