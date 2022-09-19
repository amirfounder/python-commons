import time
from typing import Optional, Callable

import requests


class HttpClient:
    def __init__(self, base_url: str, *, proxies=None, base_params=None, apply_proxies: bool = False,
                 run_with_retries: bool = False):
        self.apply_proxies = apply_proxies
        self.base_url = base_url
        self.base_params = base_params or {}
        self.proxies = proxies or {}
        self.retries_data = {}
        self.bearer_token = None
        self.run_with_retries = run_with_retries

    def _apply_proxies_options(self, request_kwargs):
        if self.proxies:
            request_kwargs['proxies'] = self.proxies

    def _apply_auth_header(self, request_kwargs):
        if self.bearer_token:
            request_kwargs['headers'] = {'Authorization': f'Bearer {self.bearer_token}'}

    def _run_with_retries(
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

    def execute_request(
            self,
            func: Callable,
            args: tuple,
            kwargs: dict,
            *,
            run_with_retries: bool = False,
            apply_proxies: bool = None,
            apply_auth_header: bool = None
    ):
        if apply_auth_header is None:
            apply_auth_header = True

        if apply_proxies is None:
            apply_proxies = self.apply_proxies

        if apply_auth_header:
            self._apply_auth_header(kwargs)

        if apply_proxies:
            self._apply_proxies_options(kwargs)

        if run_with_retries:
            kwargs = {'func': func, 'args': args, 'kwargs': kwargs}
            func = self._run_with_retries
        
        return func(**kwargs)

    def get(
            self,
            filters: dict = None,
            page: int = 1,
            size: int = 20,
            *,
            endpoint_suffix: str = '',
            run_with_retries: bool = False
    ):
        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix

        filters = filters or {}

        params = self.base_params.copy()
        params.update(filters)
        params.update({'page': page, 'size': size})

        kwargs = {'url': url, 'params': params}

        return self.execute_request(
            func=requests.get,
            args=(),
            kwargs=kwargs,
            run_with_retries=run_with_retries
        )

    def get_by_id(self, resource_id: int, *, endpoint_suffix: str = None, run_with_retries: bool = False):
        if resource_id is None:
            raise Exception('ID cannot be None')

        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix

        url += f'/{resource_id}'

        kwargs = {'url': url}

        return self.execute_request(
            func=requests.get,
            args=(),
            kwargs=kwargs,
            run_with_retries=run_with_retries
        )

    def put(self, data: Optional[dict], *, endpoint_suffix: str = None, run_with_retries: bool = False):
        if 'id' not in data:
            raise Exception('ID not provided')

        if data['id'] is None:
            raise Exception('ID cannot be None')

        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix

        url += f'/{data["id"]}'

        kwargs = {'url': url, 'data': data}
        return self.execute_request(
            func=requests.put,
            args=(),
            kwargs=kwargs,
            run_with_retries=run_with_retries
        )

    def post(self, data: Optional[dict], *, endpoint_suffix: str = None, run_with_retries: bool = False):
        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix

        kwargs = {'url': url, 'data': data}
        return self.execute_request(
            func=requests.post,
            args=(),
            kwargs=kwargs,
            run_with_retries=run_with_retries
        )

    def delete(self, resource_id: int, *, endpoint_suffix: str = None, run_with_retries: bool = False):
        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix

        url += f'/{resource_id}'

        kwargs = {'url': url}
        return self.execute_request(
            func=requests.delete,
            args=(),
            kwargs=kwargs,
            run_with_retries=run_with_retries
        )
