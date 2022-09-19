import time
from typing import Optional, Callable

import requests
from requests import Response

from commons.logging import log_info
from commons.rest_api.http_exceptions import BadGatewayException


class HttpResourceClient:
    """Enhanced request methods for REST apis"""
    def __init__(
            self,
            base_url: str,
            *,
            proxies=None,
            base_params=None,
            should_apply_proxy_options: bool = False,
            retry_count: int = 3,
    ):
        self.base_url = base_url
        self.base_params = base_params or {}
        self.bearer_token = None
        self.proxies = proxies or {}
        self.should_apply_proxy_options = should_apply_proxy_options
        self.retry_logs = {}
        self.retry_count = retry_count

    def before_request(self, func: Callable, args, kwargs):
        if self.should_apply_proxy_options and self.proxies:
            kwargs['proxies'] = self.proxies

        if self.bearer_token:
            kwargs['headers'] = {'Authorization': f'Bearer {self.bearer_token}'}

    def after_request(self, response: Response):
        return response

    def execute_request(self, func: Callable, args: tuple, kwargs: dict) -> requests.Response:
        self.before_request(func, *args, **kwargs)

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

        return self.after_request(response)

    def get(
            self,
            filters: dict = None,
            page: int = 1,
            size: int = 20,
            *,
            endpoint_suffix: str = '',
            **kwargs
    ):
        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix

        filters = filters or {}
        params = self.base_params.copy()
        params.update(filters)
        params.update({'page': page, 'size': size})

        kwargs.update({'url': url, 'params': params})
        return self.execute_request(func=requests.get, args=(), kwargs=kwargs)

    def get_by_id(self, resource_id: int, *, endpoint_suffix: str = None, **kwargs):
        if resource_id is None:
            raise Exception('ID cannot be None')

        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix
        url += f'/{resource_id}'

        kwargs.update({'url': url})
        return self.execute_request(func=requests.get, args=(), kwargs=kwargs)

    def put(self, data: Optional[dict], *, endpoint_suffix: str = None, **kwargs):
        if 'id' not in data:
            raise Exception('ID not provided')
        if data['id'] is None:
            raise Exception('ID cannot be None')

        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix
        url += f'/{data["id"]}'

        kwargs.update({'url': url, 'json': data})
        return self.execute_request(func=requests.put, args=(), kwargs=kwargs)

    def post(self, data: Optional[dict], *, endpoint_suffix: str = None, **kwargs):
        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix

        kwargs.update({'url': url, 'json': data})
        return self.execute_request(func=requests.post, args=(), kwargs=kwargs)

    def delete(self, resource_id: int, *, endpoint_suffix: str = None, **kwargs):
        url = self.base_url
        if endpoint_suffix:
            url += endpoint_suffix
        url += f'/{resource_id}'

        kwargs.update({'url': url})
        return self.execute_request(func=requests.delete, args=(), kwargs=kwargs)
