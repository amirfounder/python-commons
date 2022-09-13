import time
from abc import ABC

import requests


class BaseHttpResourceProxy(ABC):
    def __init__(self, base_url: str, endpoint: str, *, proxies=None, base_params=None):
        self.proxies = proxies or {}
        self.base_params = base_params or {}
        self.endpoint = endpoint
        self.retries_data = {}
        self.base_url = f'{base_url}{endpoint}'

    def _load_proxies_options(self, request_kwargs):
        if self.proxies:
            request_kwargs['proxies'] = self.proxies

    def run_with_retries(
            self,
            func,
            *,
            args: tuple = None,
            kwargs: dict = None,
            retry_count: int = 3,
            retry_delay: int = 1
    ):
        args = args or ()
        kwargs = kwargs or {}

        for i in range(retry_count):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f'Exception occurred: {str(e)}')
            time.sleep(retry_delay)

    def execute_request(self, func, args, kwargs, *, run_with_retries: bool = False):
        if run_with_retries:
            kwargs = {'func': func, 'args': args, 'kwargs': kwargs}
            func = self.run_with_retries
        
        return func(**kwargs)

    def get_all(self, filters: dict = None, page: int = 1, size: int = 20, *, run_with_retries: bool = False):
        filters = filters or {}
        params = self.base_params.copy()
        params.update(filters)
        params.update({'page': page, 'size': size})

        kwargs = {'url': self.base_url, 'params': params}
        self._load_proxies_options(kwargs)
        return self.execute_request(requests.get, (), kwargs, run_with_retries=run_with_retries)

    def get_by_id(self, resource_id: int, *, run_with_retries: bool = False):
        if resource_id is None:
            raise Exception('ID cannot be None')

        kwargs = {'url': f'{self.base_url}/{resource_id}'}
        self._load_proxies_options(kwargs)
        return self.execute_request(requests.get, (), kwargs, run_with_retries=run_with_retries)

    def put(self, data: dict, *, run_with_retries: bool = False):
        if 'id' not in data:
            raise Exception('ID not provided')
        if data['id'] is None:
            raise Exception('ID cannot be None')

        kwargs = {'url': f'{self.base_url}/{data["id"]}', 'data': data}
        self._load_proxies_options(kwargs)
        return self.execute_request(requests.put, (), kwargs, run_with_retries=run_with_retries)

    def post(self, data: dict, *, run_with_retries: bool = False):
        kwargs = {'url': self.base_url, 'data': data}
        self._load_proxies_options(kwargs)
        return self.execute_request(requests.post, (), kwargs, run_with_retries=run_with_retries)

    def delete(self, resource_id: int, *, run_with_retries: bool = False):
        kwargs = {'url': f'{self.base_url}/{resource_id}'}
        self._load_proxies_options(kwargs)
        return self.execute_request(requests.delete, (), kwargs, run_with_retries=run_with_retries)
