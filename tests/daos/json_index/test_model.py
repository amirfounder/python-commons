from commons.helpers.datetime import now
from commons.daos.json_index import AbstractJsonIndexModel

class Model(AbstractJsonIndexModel):
    def __init__(self):
        super().__init__()
        self.num = 1
        self.str = 'hello'
        self.time = now()


def test_model():
    model = Model()
    model.submodel = Model()
    d = dict(model)
    print(d)
