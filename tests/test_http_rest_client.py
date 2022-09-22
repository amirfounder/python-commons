import unittest
from unittest.mock import MagicMock, patch
from requests import Response

from commons.http_rest_client import HttpRestClient

class TestHTTPRestClient(unittest.TestCase):
    def test_single_execution(self):
        dummy_response = Response()
        dummy_response.status_code = 200
        dummy_response.raise_for_status = MagicMock(return_value=None)

        client = HttpRestClient(base_url='http://localhost:8000')
        session = client.make_session()

        with patch.object(session, 'get', return_value=dummy_response) as mock_get:

            def _func():
                url = client.make_url(append_suffix='/1')
                return session.get(url)

            client.execute(_func)

        mock_get.assert_called()

    def test_single_execution_failed_3_times(self):
        def _raise_for_status():
            raise Exception('test')

        dummy_response = Response()
        dummy_response.status_code = 200
        dummy_response.raise_for_status = _raise_for_status

        client = HttpRestClient(base_url='http://localhost:8000')
        session = client.make_session()

        with patch.object(session, 'get', return_value=dummy_response) as mock_get:

            def _func():
                url = client.make_url(append_suffix='/1')
                return session.get(url)

            try:
                client.execute(_func)
            except Exception as e:
                if str(e) != 'test':
                    raise e

        assert mock_get.call_count == 3

    def test_executions_in_threads(self):
        client = HttpRestClient(base_url='http://localhost:8000')
        sess = client.make_session()

        funcs = []
        for i in range(20):
            def _func():
                url = client.make_url(append_suffix=f'/{i}')
                return sess.get(url)

            funcs.append(_func)

        client.execute_in_thread_pool(funcs, max_threads=20)

    def test_execute_in_thread_pool(self):
        client = HttpRestClient(base_url='http://localhost:8000')
        sess = client.make_session()
        funcs = []

        dummy_response = Response()
        dummy_response.status_code = 200
        dummy_response.raise_for_status = MagicMock(return_value=None)

        mock_gets = []

        for i in range(20):
            def func():
                with patch.object(sess, 'get', return_value=dummy_response) as mock_get:
                    mock_gets.append(mock_get)
                    url = client.make_url(append_suffix=f'/1')
                    return sess.get(url)
            funcs.append(func)

        client.execute_in_thread_pool(funcs, max_threads=20)

        assert len(mock_gets) == 20
        assert all([mock_get.call_count == 1 for mock_get in mock_gets])
