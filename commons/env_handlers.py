from os import environ


_DEV = 'dev'
_PROD = 'prod'
_STAGING = 'staging'
_QA = 'qa'
_ENV_KEY = 'ENVIRONMENT'


def configure_environment_key(key):
    global _ENV_KEY
    _ENV_KEY = key


def set_env_to_prod():
    environ[_ENV_KEY] = _PROD


def set_env_to_staging():
    environ[_ENV_KEY] = _STAGING


def set_env_to_qa():
    environ[_ENV_KEY] = _QA


def set_env_to_dev():
    environ[_ENV_KEY] = _DEV


def get_working_env(default: str = None):
    return environ.get(_ENV_KEY, default)


def is_env_prod():
    return get_working_env() == _PROD


def is_env_staging():
    return get_working_env() == _STAGING


def is_env_qa():
    return get_working_env() == _QA


def is_env_dev():
    return get_working_env() == _DEV

