from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from typing import Type, Dict, Callable

from commons import format_iso, parse_iso, get_attributes, now, safe_cast


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

    @classmethod
    def get_encoder(cls, klass):
        return cls._encoders.get(klass)

    @classmethod
    def register_encoder(cls, klass, encoder):
        cls._encoders[klass] = encoder


class DecoderRegistry:
    _decoders: Dict[Type, Callable] = {
        datetime: parse_iso
    }

    @classmethod
    def get_decoder(cls, klass):
        return cls._decoders.get(klass)

    @classmethod
    def register_decoder(cls, klass, decoder):
        cls._decoders[klass] = decoder


class ModelToDictCodec:
    _codec: Dict[Type, CodecModel] = defaultdict(dict)

    @classmethod
    def _encode(cls, klass, key, value):
        model_key = ModelKey(klass, key, type(value))
        cls._codec[klass][key] = model_key
        return model_key.encode(value)

    @classmethod
    def encode(cls, value):
        if encoder := EncoderRegistry.get_encoder(type(value)):
            return encoder(value)

    @classmethod
    def decode(cls, klass, key, value):
        model_key = cls._codec[klass][key]
        return model_key.decode(value)

    @classmethod
    def register_model(cls, klass):
        pass

    @classmethod
    def register_key(cls, klass, key, value_type):
        pass


class ModelKey:
    __slots__ = ('klass', 'key', 'value_type', 'encoder', 'decoder')

    def __init__(self, klass, key, value_type):
        self.klass, self.key, self.value_type = klass, key, value_type
        self.encoder = EncoderRegistry.get_encoder(value_type)
        self.decoder = DecoderRegistry.get_decoder(value_type)

    def encode(self, value):
        return self.encoder(value) if self.encoder else value

    def decode(self, value):
        return self.decoder(value) if self.decoder else value


class CodecModel:
    __slots__ = ('encoder', 'decoder', 'keys')

    def __init__(self, encoder, decoder, keys):
        self.encoder = encoder
        self.decoder = decoder,
        self.keys = keys


class JsonEncodeable:
    def __init_subclass__(cls, **kwargs):
        EncoderRegistry.register_encoder(cls, cls.to_dict)
        DecoderRegistry.register_decoder(cls, cls.from_dict)

    def to_dict(self):
        obj = {}
        for key, value in get_attributes(self):
            obj[key] = ModelToDictCodec.encode(type(self), key, value)
        return obj

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, obj: Dict):
        self = cls()
        for key, value in obj.items():
            setattr(self, key, ModelToDictCodec.decode(cls, key, value))
        return self

    @classmethod
    def from_json(cls, obj: str):
        return cls.from_dict(json.loads(obj))


class FluidModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, '__slots__') and k not in getattr(self, '__slots__'):
                continue
            setattr(self, k, v)


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
