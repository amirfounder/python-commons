from unittest import TestCase

from commons.ioc import service, get_service


class TestIOC(TestCase):
    def test_basic_injection(self):

        @service
        class ServiceFoo:
            def __init__(self):
                pass

        @service
        class ServiceBar:
            def __init__(self):
                self.foo = get_service(ServiceFoo)
                self.bar = 'Bar'

        bar = get_service(ServiceBar)

        self.assertIsInstance(bar, ServiceBar)
        self.assertIsInstance(bar.foo, ServiceFoo)
