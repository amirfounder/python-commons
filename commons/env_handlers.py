from os import environ


def set_env_to_prod():
    environ['ENVIRONMENT'] = 'prod'


def set_env_to_dev():
    environ['ENVIRONMENT'] = 'dev'


def get_working_env(default: str = None):
    return environ.get('ENVIRONMENT', default)


def is_env_prod():
    return get_working_env() == 'prod'


def is_env_dev():
    return get_working_env() == 'dev'

