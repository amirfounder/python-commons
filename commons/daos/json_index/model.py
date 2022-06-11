from __future__ import annotations
from datetime import datetime
from typing import Dict, Union, Optional, Type, Callable

from commons.utils import get_attributes, unique_type_set_from_list, this_if_none
from commons.helpers import json, parse_iso, format_iso
from commons.mixins import Mapping


_DEFAULT_ENCODERS_DECODERS = [
    (datetime, format_iso, parse_iso)
]


class CodecModelKeyFactory:
    def __init__(self, codec):
        self.codec = codec
        self.type_map = (
            ({list, set, tuple}, CodecModelIterKey),
            ({dict}, CodecModelDictKey)
        )

    def create(self, cls, key, value):
        value_type = type(value)
        default_model_key = CodecModelKey

        for value_type_set, model_key in self.type_map:
            if value_type in value_type_set:
                return model_key(cls, key, value)

        return default_model_key(cls, key, value_type)


class Codec(Mapping, key='_codec'):
    def __init__(self):
        self._codec: Dict[Type, CodecModel] = {}
        self.encoders: Dict[Type, Callable] = {}
        self.decoders: Dict[Type, Callable] = {}
        self.model_key_factory = CodecModelKeyFactory(self)

    def load_default_encoders_decoders(self):
        for type_, encoder, decoder in _DEFAULT_ENCODERS_DECODERS:
            self.register_encoder_decoder(type_, encoder, decoder)

    def get_codec_model_key(self, cls, key, value) -> Optional[CodecModelKey]:
        if codec_model := self.get(cls):
            if key not in codec_model:
                codec_model[key] = _codec.model_key_factory.create(cls, key, value)
            return codec_model[key]

    def get_encoder(self, type_: Type, key: str):
        if type_ in self:
            if key in self[type_]:
                if self[type_][key].encoder:
                    return self[type_][key].encoder

        if type_ in self.encoders:
            return self.encoders[type_]

        return lambda o: o

    def get_decoder(self, type_, key):
        if type_ in self:
            if key in self[type_]:
                if self[type_][key].decoder:
                    return self[type_][key].decoder

        if type_ in self.decoders:
            return self.decoders[type_]

        return lambda o: o

    def encode(self, cls, key, value):
        return self.get_encoder(cls, key)(value)

    def decode(self, cls, key, value):
        return self.get_decoder(cls, key)(value)

    def register_json_encodeable(self, cls):
        self[cls] = CodecModel(cls, cls.to_dict, cls.from_dict)

    def register_encoder_decoder(self, type_, encoder, decoder):
        self.encoders[type_] = encoder
        self.decoders[type_] = decoder


class CodecModel(Mapping, key='keys'):
    __slots__ = ('cls', 'encoder', 'decoder', 'keys')

    def __init__(self, cls, encoder, decoder):
        self.cls = cls
        self.encoder = encoder
        self.decoder = decoder
        self.keys = {}

    def register(self, cls, key, value):
        self[key] = _codec.model_key_factory.create(cls, key, value)


class CodecModelKey:
    __slots__ = ('cls', 'key', 'value_type', 'encoder', 'decoder')

    def __init__(self, cls, key, value_type):
        self.cls = cls
        self.key = key
        self.value_type = value_type
        self.encoder = _codec[value_type].encoder if value_type in _codec else None
        self.decoder = _codec[value_type].decoder if value_type in _codec else None


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
            _codec.register_json_encodeable(cls)

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
