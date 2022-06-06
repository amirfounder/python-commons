import os
from threading import current_thread
from typing import Optional

from commons.file_handlers import safe_write
from commons.datetime_handlers import now
from commons.env_handlers import get_working_env


PATH = None

def configure_path(path: str):
    global PATH
    PATH = path


def _log(message, level: str = 'info'):
    if PATH is None:
        raise Exception('Please configure path using logging_handlers.configure_path(...) before attempting to log.')

    timestamp = now().isoformat().ljust(40)
    env = 'ENV: ' + str(get_working_env()).upper().ljust(10)
    pid = 'PID: ' + str(os.getpid()).ljust(15)
    thread = 'THREAD: ' + current_thread().name.ljust(25)
    level = 'LEVEL: ' + level.upper().ljust(15)

    message = timestamp + env + pid + thread + level + message

    print(message)
    safe_write(PATH, message + '\n', mode='a')


def info(message):
    _log(message, 'info')


def error(message: str, exception: Optional[Exception] = None):
    if exception:
        message = message.strip().removesuffix('.') + f'. {type(exception).__name__} Exception: {str(exception)}'
    _log(message, 'error')


def success(message):
    _log(message, 'success')