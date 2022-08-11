from os import environ


DEV = 'dev'
PROD = 'prod'
STAGING = 'staging'
QA = 'qa'
ENV_KEY = 'ENVIRONMENT'


def configure_environment_key(key):
    global ENV_KEY
    ENV_KEY = key


def set_env_to_prod():
    environ[ENV_KEY] = PROD


def set_env_to_staging():
    environ[ENV_KEY] = STAGING


def set_env_to_qa():
    environ[ENV_KEY] = QA


def set_env_to_dev():
    environ[ENV_KEY] = DEV


def get_working_env(default: str = None):
    return environ.get(ENV_KEY, default)


def is_env_prod():
    return get_working_env() == PROD


def is_env_staging():
    return get_working_env() == STAGING


def is_env_qa():
    return get_working_env() == QA


def is_env_dev():
    return get_working_env() == DEV

