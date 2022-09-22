import time
from typing import Optional, Callable, TypeVar, Iterable

import requests
from requests import Response

from commons.logging import log_info
from commons.rest_api.http_exceptions import BadGatewayException
from commons.threads import ThreadWrapper, start_threads, join_threads

_T = TypeVar('_T')


class HttpRestClient:
    def __init__(
            self,
            base_url: str = None,
            base_params: dict = None,
            base_headers: dict = None,
            proxies: dict = None,
            *,
            bearer_token: str = None,
            base_retry_count: int = 3,
            base_retry_delay: int = 1,
    ):
        self.base_url = base_url
        self.base_params = base_params or {}
        self.base_headers = base_headers or {}
        self.proxies = proxies or {}
        self.bearer_token = bearer_token
        self.base_retry_count = base_retry_count
        self.base_retry_delay = base_retry_delay

    def execute(
            self,
            executable: Callable[[], requests.Response],
            *,
            retry_count: int = None,
            retry_delay: int = None,
    ) -> requests.Response:
        retry_count = retry_count or self.base_retry_count
        retry_delay = retry_delay or self.base_retry_delay

        for i in range(retry_count):
            try:
                response = executable()
                response.raise_for_status()
                return response

            except Exception as e:
                if i == retry_count - 1:
                    raise e
                time.sleep(retry_delay * (i + 1))

    def execute_in_thread_pool(
            self,
            funcs: Iterable[Callable[[], Response]],
            *,
            retry_count: int = 3,
            max_threads: int = 25
    ) -> requests.Response:
        threads = []

        for func in funcs:
            def _func():
                return self.execute(func, retry_count=retry_count)

            t = ThreadWrapper(target=_func)
            threads.append(t)

        start_threads(threads, max_threads=max_threads)
        join_threads(threads)

        for t in threads:
            yield t.result

    def make_url(self, append_suffix: str | int = None):
        url = self.base_url

        if not url:
            raise ValueError('base_url is not set')

        if append_suffix:
            if not isinstance(append_suffix, str):
                append_suffix = str(append_suffix)
            if not url.startswith('/'):
                url = '/' + url
            url += append_suffix

        return url

    def make_session(self, headers: dict = None, params: dict = None):
        sess = requests.Session()

        sess.headers.update(self.base_headers)
        sess.headers.update(headers or {})

        if self.bearer_token:
            sess.headers['Authorization'] = f'Bearer {self.bearer_token}'

        sess.params.update(self.base_params)
        sess.params.update(params or {})

        sess.proxies.update(self.proxies or {})

        return sess


class _DeprecatedHttpRestClient:
    def __init__(
            self,
            base_url: str,
            *,
            proxies=None,
            base_params=None,
            retry_count: int = 3,
            bearer_token: str = None
    ):
        self.base_url = base_url
        self.base_params = base_params or {}
        self.proxies = proxies or {}
        self.retry_count = retry_count

        self.bearer_token = bearer_token
        self.retry_logs = {}

    def before_request(self, func: Callable, args, kwargs):
        if self.proxies:
            kwargs['proxies'] = self.proxies

        if self.bearer_token:
            if 'headers' not in kwargs:
                kwargs['headers'] = {}
            kwargs['headers']['Authorization'] = f'Bearer {self.bearer_token}'

        return func, args, kwargs

    def _execute_request(self, func: Callable, args: tuple, kwargs: dict) -> requests.Response:
        func, args, kwargs = self.before_request(func, args, kwargs)

        response = None
        is_success = False

        for i in range(3):
            try:
                response = func(*args, **kwargs)
                response.raise_for_status()
                is_success = True
                break

            except Exception as e:

                if 'exceptions' not in self.retry_logs:
                    self.retry_logs['exceptions'] = []
                self.retry_logs['exceptions'].append(e)

                delay = 2 ** i
                log_info(f'Suppressed exception: {str(e)}. Re-attempting in {delay} seconds...')
                time.sleep(delay)

        if not is_success:
            raise BadGatewayException('Bad gateway')

        return response

    def get(
            self,
            filters: dict = None,
            page: int = 1,
            size: int = 20,
            *,
            endpoint_suffix: str = '',
            **kwargs
    ):
        url = f'{self.base_url}{endpoint_suffix}'
        filters = filters or {}
        params = self.base_params.copy()
        params.update(filters)
        params.update({'page': page, 'size': size})

        kwargs.update({'url': url, 'params': params})
        return self._execute_request(func=requests.get, args=(), kwargs=kwargs)

    def get_by_id(self, resource_id: int, *, endpoint_suffix: str = '', **kwargs):
        if resource_id is None:
            raise Exception('ID cannot be None')

        url = f'{self.base_url}{endpoint_suffix}/{resource_id}'
        kwargs.update({'url': url})
        return self._execute_request(func=requests.get, args=(), kwargs=kwargs)

    def put(self, json: Optional[dict] = None, *, endpoint_suffix: str = '', **kwargs):
        if 'id' not in json:
            raise Exception('ID not provided')
        if json['id'] is None:
            raise Exception('ID cannot be None')

        url = f'{self.base_url}{endpoint_suffix}/{json["id"]}'
        kwargs.update({'url': url, 'json': json})
        return self._execute_request(func=requests.put, args=(), kwargs=kwargs)

    def post(self, json: Optional[dict] = None, *, endpoint_suffix: str = '', **kwargs):
        url = f'{self.base_url}{endpoint_suffix}'
        kwargs.update({'url': url, 'json': json})
        return self._execute_request(func=requests.post, args=(), kwargs=kwargs)

    def delete(self, resource_id: int, *, endpoint_suffix: str = '', **kwargs):
        url = f'{self.base_url}{endpoint_suffix}/{resource_id}'
        kwargs.update({'url': url})
        return self._execute_request(func=requests.delete, args=(), kwargs=kwargs)
