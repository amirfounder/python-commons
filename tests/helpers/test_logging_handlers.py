from python_commons.helpers.logging import log_error, configure_logging_path


def test_log_error_happy_path():
    configure_logging_path('tests/data/logs.txt')
    log_error('This is a test')
    configure_logging_path(None)


def test_log_error_sad_path_no_path_configured():
    try:
        log_error('This is a test')
    except Exception as e:
        assert str(e) == 'Configure path using logging_handlers.configure_path(...) before attempting to log.'
