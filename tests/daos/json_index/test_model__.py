from __future__ import annotations

import json
from datetime import datetime
from typing import Type, Dict, Callable, Optional, Union

from commons import format_iso, parse_iso, get_attributes, now, this_if_none, unique_type_set_from_list
from commons.mixins import FluidModel, MappingModel

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


class EncoderRegistry(MappingModel, key='_encoders'):
    _encoders: Dict[Type, Callable] = {
        datetime: format_iso,
    }


class DecoderRegistry(MappingModel, key='_decoders'):
    _decoders: Dict[Type, Callable] = {
        datetime: parse_iso
    }


class CodecModelKeyFactory:
    def __init__(self, codec):
        self.codec = codec
        self.type_map = (
            ({list, set, tuple}, CodecModelIterKey),
            ({dict}, CodecModelDictKey)
        )
    
    def create(self, cls, key, value):
        value_type = type(value)
        for value_type_set, constructor in self.type_map:
            if value_type in value_type_set:
                return constructor(cls, key, value)
        return CodecModelKey(cls, key, value_type)


class Codec(MappingModel, key='_codec'):
    def __init__(self):
        self._codec = {}
        self.encoders = EncoderRegistry()
        self.decoders = DecoderRegistry()
        self.model_key_factory = CodecModelKeyFactory(self)

    def _get_codec_model_key(self, cls, key, value) -> Optional[CodecModelKey]:
        if codec_model := self.get(cls):
            if key not in codec_model:
                codec_model[key] = _codec.model_key_factory.create(cls, key, value)
            return codec_model[key]

    def encode(self, cls, key, value):
        if (cm_key := self._get_codec_model_key(cls, key, value)) and cm_key.encoder:
            return cm_key.encoder(value)
        return value

    def decode(self, cls, key, value):
        if (cm_key := self._get_codec_model_key(cls, key, value)) and cm_key.decoder:
            return cm_key.decoder(value)
        return value

    def register(self, cls, encoder, decoder):
        self[cls] = CodecModel(cls, encoder, decoder)


class CodecModel(MappingModel, key='keys'):
    __slots__ = ('cls', 'encoder', 'decoder', 'keys')

    def __init__(self, cls, encoder, decoder, keys=None):
        self.cls = cls
        self.encoder = encoder
        self.decoder = decoder
        self.keys = this_if_none(keys, {})

    def register(self, cls, key, value):
        self[key] = _codec.model_key_factory.create(cls, key, value)


class CodecModelKey:
    __slots__ = ('cls', 'key', 'value_type', 'encoder', 'decoder')
    
    def __init__(self, cls, key, value_type):
        self.cls = cls
        self.key = key
        self.value_type = value_type
        self.encoder = None
        self.decoder = None
        self.register_encoder_decoder()

    def register_encoder_decoder(self):
        if codec_model := _codec.get(self.value_type):
            self.encoder = codec_model.encoder
            self.decoder = codec_model.decoder


class CodecModelIterKey:
    __slots__ = ('cls', 'key', 'decoded_iter_type', 'decoded_iter_is_empty', 'codec_model_key', 'type')

    def __init__(self, cls, key, iter_: Union[list, set, tuple]):
        self.validate_iter(iter_)
        self.cls = cls
        self.key = key
        self.decoded_iter_type = type(iter_)
        self.codec_model_key = _codec.model_key_factory.create(type(iter_), None, next(iter(iter_), None))
    
    @staticmethod
    def validate_iter(list_):
        if len(unique_type_set_from_list(list_)) > 2:
            raise Exception('Cannot have more than 1 type in JSONEncodeable list')

    def encoder(self, value):
        return [self.codec_model_key.encoder(item) for item in value]

    def decoder(self, value):
        res = [self.codec_model_key.decoder(item) for item in value]
        return self.decoded_iter_type(res)


class CodecModelDictKey:
    def __init__(self, cls, key, value):
        pass


_codec = Codec()


class JsonEncodeable:
    def __init_subclass__(cls, **kwargs):
        if cls not in _codec:
            _codec.register(cls, cls.to_dict, cls.from_dict)

    def to_dict(self):
        obj, cls = {}, type(self)
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
