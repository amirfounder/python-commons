import inspect
from inspect import getmembers
from datetime import datetime

from commons.helpers import now


class Model:
    created_at: datetime = lambda v: now()
    updated_at: datetime


if __name__ == '__main__':
    model = Model()
    print(model)
