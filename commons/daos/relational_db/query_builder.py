from __future__ import annotations
from datetime import datetime
from typing import Type, Any, List


class Table:
    def __init__(self, name):
        self.name = name
        self._columns = []

    @property
    def columns(self):
        for column in self._columns:
            yield column


class Comparable:
    def __eq__(self, other):
        return Condition(self).eq(other)

    def eq(self, value):
        return Condition(self).eq(value)

    def ne(self, value):
        return Condition(self).ne(value)

    def lt(self, value):
        return Condition(self).lt(value)

    def lte(self, value):
        return Condition(self).lte(value)

    def gt(self, value):
        return Condition(self).gt(value)

    def gte(self, value):
        return Condition(self).gte(value)


class Joinable:
    def on(self, other: Joinable):
        self.other = other


class Column(Comparable, Joinable):
    def __init__(self, type_: Type):
        self._type = type_


class Car(Table):
    id = Column(int)
    make = Column(str)
    model = Column(str)
    year = Column(datetime)

    def __init__(self):
        super().__init__('cars')


class Person(Table):
    id = Column(int)
    primary_car_id = Column(int)

    def __init__(self):
        super().__init__('people')


class SqlBuilder:
    def __init__(self):
        self.stack = []
        self.clauses = []
        self.joins = []

    def select(self, *args):
        stmt = _Select(self, *args)
        self.stack.append(stmt)
        return self

    def where(self, *args):
        self.clauses.append(Where(self, *args))
        return self

    def inner_join(self, *args):
        self.joins.append(InnerJoin(self, *args))
        return self

    def distinct(self):
        self.stack.append('DISTINCT')
        return self

    def build(self):
        return ' '.join(self.stack)


class Statement:
    def __init__(self, *args):
        pass

    def execute(self):
        pass


class _Select:
    def __init__(self, builder, *args: List[Column | Table]):
        self._builder = builder
        self.args = args
        self.clauses = []
        self.joins = []

    def where(self, *args):
        self._builder.where(*args)

    def inner_join(self, *args):
        self.joins.append(InnerJoin(*args))


class InnerJoin:
    def __init__(self, *args):
        self.args = args


class Where:
    def __init__(self, builder,  condition: Condition):
        self._builder = builder
        self.condition = condition


class Condition:
    def __init__(self, column: Comparable):
        self.column = column
        self.operator = None
        self.value = None
        self.next_condition = None

    def and_(self, *args):
        self.next_condition = Condition(*args)
        return self.next_condition

    def _set_operator_value(self, operator: str, value: Any):
        self.operator = operator
        self.value = value
        return self

    def like(self, value):
        return self._set_operator_value('LIKE', value)

    def eq(self, value):
        return self._set_operator_value('EQ', value)

    def lt(self, value):
        return self._set_operator_value('LT', value)

    def lte(self, value):
        return self._set_operator_value('LTE', value)

    def gt(self, value):
        return self._set_operator_value('GT', value)

    def gte(self, value):
        return self._set_operator_value('GTE', value)

    def ne(self, value):
        return self._set_operator_value('NE', value)


class ConditionalOr:
    def __init__(self, *args: Condition | ConditionalAnd):
        self.args = args


class ConditionalAnd:
    def __init__(self, *args: Condition | ConditionalOr):
        self.args = args


class Select(SqlBuilder):
    def __new__(cls, *args, **kwargs):
        return super().__init__().select(*args)


def test_builder():
    statement = (
        Select(Car)
        .where(
            ConditionalOr(
                ConditionalAnd(
                    Car.model.eq('Honda'),
                    Car.make.eq('Civic')
                ),
                ConditionalAnd(
                    Car.model.eq('Tesla'),
                    Car.make.eq('Table E')
                )
            )
        )
        .distinct()
        .build()
    )

    stmt = (
        Select(Car, Person)
        .where((Car.model == 'Accord' and Car.make == 'Honda') or (Car.model == 'Table E' and Car.make == 'Tesla'))
        .inner_join(Car.id.on(Person.primary_car_id))
    )

    stmt = Select(Car, Person)\
        .where(Car.model == 'Accord' and Car.make == 'Honda')\
        .inner_join(Car.id.on(Person.primary_car_id))\
        .distinct()
    
    stmt = Select(Car, Person).where(Car.model == 'Accord').inner_join(Car.id, Person.primary_car_id)
