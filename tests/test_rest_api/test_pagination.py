from unittest import TestCase

from commons.rest_api.pagination import PaginatedResults, PaginationOptions

class TestPagination(TestCase):
    def test_constructor(self):
        PaginatedResults(
            results=[],
            params=PaginationOptions(page=1, size=10).dict(),
            count=0
        )
