from __future__ import annotations

from commons.daos.json_index import JsonEncodeable
from commons.helpers import now
from commons.mixins import FluidInitializer

'''
Codec = Codec(
    Recruiter: CodecModel(
        encoder: '...',
        decoder: '...',
        keys: {
            'age': CodecModelKey(int, ...),
            'name': CodecModelKey(str, ...),
            'dog': CodecModelKey(Dog, encoder=Codec[Dog].encoder, ...),
            'dogs': CodecModelIterKey(
                type = list
                child_type = CodecModelKey(type=Dog,encoder=Codec[Dog].encoder, ...)
                encoder = Encoder
            )
            'map': CodecModelDictKey(
                type = dict
                encode=lambda o: {k:v for k,v, in self.items()}
                keys = {
                    'yes': CodecModelKey(),
                    'no': CodecModelKey()
                }
            )
        }
    ),
    Dog: CodecModel(
        encoder: '...',
        decoder: '...',
        keys: {...}
    ),
    list: CodecModel(
        encoder: lambda prev_key, model: ...,
        decoder: lambda prev_key, obj: ...,
    ),
    dict: CodecModel(
        encoder: ...
    )
)
'''
class Recruiter(FluidInitializer, JsonEncodeable):
    pass


class Pet(FluidInitializer, JsonEncodeable):
    pass


class Dog(FluidInitializer, JsonEncodeable):
    pass


class Cat(FluidInitializer, JsonEncodeable):
    pass


def test_models():
    recruiter = Recruiter(
        name='Amir',
        age=3,
        cat=Cat(name='Whiskers'),
        dogs=[
            Dog(name='Pepper'),
            Dog(name='Dolly', age=3, born=now())
        ]
    )
    d = recruiter.to_dict()
    r = Recruiter.from_dict(d)
    print(r)
