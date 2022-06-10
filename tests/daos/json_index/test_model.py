from datetime import datetime

from commons import now, parse_iso, format_iso
from commons.daos.json_index.model import Key, AbstractModel, set_default_jsonable_fns


set_default_jsonable_fns(datetime, to_jsonable=format_iso, from_jsonable=parse_iso)


class Model(AbstractModel):
    created_at = Key(datetime, default=now())
    updated_at = Key(datetime, default=now())


class TouchPoint(Model):
    value = Key(str)


class TouchPoints(AbstractModel):
    initial_connection = Key(TouchPoint)
    initial_connection_accepted = Key(TouchPoint)


class Recruiter(Model):
    name = Key(str)
    company = Key(str)
    touchpoints = Key(TouchPoints)


def test_it_works():
    recruiter = Recruiter()
    d = dict(recruiter)
    r = Recruiter(**d)
    print(d)
    print(r)
