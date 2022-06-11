from __future__ import annotations

import json
from datetime import datetime
from typing import Type, Dict, Callable

from commons import format_iso, parse_iso, get_attributes, now, safe_cast, this_if_none
from commons.mixins import FluidModel, MappingModel

'''

LOGIC: 

# CodecModelKey
class Codec:
    def __init__(self):
        self._codec = {}
        
    def encode(self, model_class, key, value):
        value_type = type(value)
        if codec_model := self._codec[model_class]:
            return codec_model.encode(value)
        return value

class CodecModel:
    def encode(self, key, value):
        value_type = type(value)
        if codec_model_key := self._keys[key]:
            return codec_model.encode(value)
        return value
        
class CodecModelKey:
    def encode(value):
        kwargs: {
            'prev_key': 'self',
            'value': 'value'
        }
        if self.type is not list:
            kwargs.pop('prev_key')
        self.model_ref.encode(value)



Codec = Codec(
    Recruiter: CodecModel(
        encoder: '...',
        decoder: '...',
        keys: {
            'age': CodecModelKey(int, encoder=None),
            'name': CodecModelKey(str, encode=None),
            'dog': CodecModelKey(Dog, encode=Codec[Dog].encode),
            'dogs': CodecModelKey(list, encoder=Codec[list].encode)
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


class EncoderRegistry:
    _encoders: Dict[Type, Callable] = {
        datetime: format_iso,
        dict: lambda o: {k: safe_cast(v, dict) for k, v in o.items()},
    }

    def get_encoder(self, klass):
        return self._encoders.get(klass)

    def register_encoder(self, klass, encoder):
        self._encoders[klass] = encoder


class DecoderRegistry:
    _decoders: Dict[Type, Callable] = {
        datetime: parse_iso
    }

    def get_decoder(self, klass):
        return self._decoders.get(klass)

    def register_decoder(self, klass, decoder):
        self._decoders[klass] = decoder


class Codec(MappingModel, key='_codec'):
    def __init__(self):
        self._codec = {}
        self.encoders = EncoderRegistry()
        self.decoders = DecoderRegistry()

    def _get_codec_model_key(self, cls, key, value_type) -> CodecModelKey:
        if cls not in self._codec:
            self._codec[cls] = {}

        codec_model = self._codec[cls]

        if key not in codec_model:
            codec_model[key] = CodecModelKey(cls, key, value_type)

        return codec_model[key]

    def encode(self, cls, key, value):
        if encode := self._get_codec_model_key(cls, key, type(value)).encoder:
            return encode(value)
        return value

    @staticmethod
    def decode(cls, key, value):
        return value


class CodecModel(MappingModel, key='keys'):
    __slots__ = ('type', 'encoder', 'decoder', 'keys')

    def __init__(self, type_, encoder, decoder, keys=None):
        self.type = type_
        self.encoder = encoder
        self.decoder = decoder,
        self.keys = this_if_none(keys, {})


class CodecModelKey:
    __slots__ = ('cls', 'key', 'type', 'encoder', 'decoder')
    
    def __init__(self, cls, key, type_):
        self.cls = cls
        self.key = key
        self.type = type_
        self.encoder = None
        self.decoder = None


_codec = Codec()


class JsonEncodeable:
    def __init_subclass__(cls, **kwargs):
        if cls not in _codec:
            _codec[cls] = CodecModel(cls, cls.to_dict, cls.from_dict, {})

    def to_dict(self):
        obj = {}
        cls = type(self)
        for key, value in get_attributes(self):
            obj[key] = _codec.encode(cls, key, value)
        return obj

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, obj: Dict):
        self = cls()
        for key, value in obj.items():
            setattr(self, key, _codec.decode(cls, key, value))
        return self

    @classmethod
    def from_json(cls, obj: str):
        return cls.from_dict(json.loads(obj))


class Recruiter(FluidModel, JsonEncodeable):
    pass


class Pet(FluidModel, JsonEncodeable):
    pass


class Dog(FluidModel, JsonEncodeable):
    pass


class Cat(FluidModel, JsonEncodeable):
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
