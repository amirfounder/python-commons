from commons.helpers.datetime import now
from commons.daos.json_index import AbstractJsonIndexModel, AbstractJsonIndexModelsDict


class Employees(AbstractJsonIndexModelsDict):
    pass


class Employee(AbstractJsonIndexModel):
    def __init__(self, name, age, has_reporters=False):
        super().__init__()
        self.name = name
        self.age = age
        self.updated_at = now()
        if has_reporters:
            self.reporters = Employees()


def test_model():
    amir = Employee('Amir', 22, True)
    jack = Employee('Jack', 24)
    amir.reporters.source[jack.name] = jack
    d = dict(amir)

    assert d['name'] == 'Amir'
    assert d['age'] == 22
    assert 'Jack' in d['reporters']
    assert d['reporters']['Jack']['name'] == 'Jack'
    assert d['reporters']['Jack']['age'] == 24
