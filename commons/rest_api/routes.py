import time
from datetime import timedelta
from typing import Callable, Coroutine, Any

from commons.logging import log_info
from fastapi.routing import APIRoute
from fastapi.requests import Request
from fastapi.responses import Response


class PerformanceLoggerRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_handler = super().get_route_handler()

        async def custom_handler(request: Request) -> Response:
            start = time.time()
            response = await original_handler(request)
            elapsed = time.time() - start

            log_info(f'PERFORMANCE LOG: {request.method} {request.url.path} {timedelta(seconds=elapsed)}')

            return response

        return custom_handler
