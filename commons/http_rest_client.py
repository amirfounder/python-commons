import time
from typing import Optional, Callable, Generic, TypeVar

import requests

from commons.logging import log_info
from commons.rest_api.http_exceptions import BadGatewayException

_T = TypeVar('_T')


class HttpRestClient(Generic[_T]):
    def __init__(
            self,
            base_url: str,
            *,
            proxies=None,
            base_params=None,
            bl_model_class=None,
            retry_count: int = 3,
    ):
        self.base_url = base_url
        self.base_params = base_params or {}
        self.proxies = proxies or {}
        self.retry_count = retry_count
        self.bl_model_class = bl_model_class

        self.bearer_token = None
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
