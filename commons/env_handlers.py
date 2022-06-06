from os import environ


DEV = 'dev'
PROD = 'prod'
STAGING = 'staging'
QA = 'qa'
ENVIRONMENT_KEY = 'ENVIRONMENT'


def configure_environment_key(key):
    global ENVIRONMENT_KEY
    ENVIRONMENT_KEY = key


def set_env_to_prod():
    environ[ENVIRONMENT_KEY] = PROD


def set_env_to_staging():
    environ[ENVIRONMENT_KEY] = STAGING


def set_env_to_qa():
    environ[ENVIRONMENT_KEY] = QA


def set_env_to_dev():
    environ[ENVIRONMENT_KEY] = DEV


def get_working_env(default: str = None):
    return environ.get(ENVIRONMENT_KEY, default)


def is_env_prod():
    return get_working_env() == PROD


def is_env_staging():
    return get_working_env() == STAGING


def is_env_qa():
    return get_working_env() == QA


def is_env_dev():
    return get_working_env() == DEV

