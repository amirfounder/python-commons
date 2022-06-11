from __future__ import annotations
from datetime import datetime
from typing import Dict, Union, Optional, Type, Callable

from commons.utils import get_attributes, unique_type_set_from_list
from commons.helpers import json, parse_iso, format_iso
from commons.mixins import Mapping


_DEFAULT_ENCODERS_DECODERS = [
    (datetime, format_iso, parse_iso)
]


def isiter(o: Union[type, list, tuple, set]):
    return (o if isinstance(o, type) else type(o)) in {list, tuple, set}


def isdict(o: Union[type, dict]):
    return (o if isinstance(o, type) else type(o)) in {dict}


def create_codec_model_key(cls, key, value):
    vt = type(value)
    if isiter(vt):
        return CodecModelIterKey(cls, key, value)
    if isdict(vt):
        return CodecModelDictKey(cls, key, value)
    return CodecModelKey(cls, key, vt)


class CodecModel(Mapping, key='keys'):
    __slots__ = ('cls', 'encoder', 'decoder', 'keys')

    def __init__(self, cls, encoder, decoder):
        self.cls = cls
        self.encoder = encoder
        self.decoder = decoder
        self.keys = {}

    def register(self, cls, key, value):
        self[key] = create_codec_model_key(cls, key, value)


class CodecModelKey:
    __slots__ = ('cls', 'key', 'value_type')

    def __init__(self, cls, key, value_type):
        self.cls = cls
        self.key = key
        self.value_type = value_type

    @property
    def encoder(self):
        if self.value_type in _codec:
            return _codec[self.value_type].encoder
        if self.value_type in _codec.encoders:
            return _codec.encoders[self.value_type]

    @property
    def decoder(self):
        if self.value_type in _codec:
            return _codec[self.value_type].decoder
        if self.value_type in _codec.decoders:
            return _codec.decoders[self.value_type]


class CodecModelIterKey:
    __slots__ = ('cls', 'key', 'decoded_iter_type', 'decoded_iter_is_empty', 'codec_model_key', 'type')

    def __init__(self, cls, key, iter_: Union[list, set, tuple]):
        self.validate_iter(iter_)
        self.cls = cls
        self.key = key
        self.decoded_iter_type = type(iter_)
        self.codec_model_key = create_codec_model_key(type(iter_), None, next(iter(iter_), None))

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


class Codec(Mapping[Type, CodecModel], key='_codec'):
    def __init__(self):
        self._codec: Dict[Type, CodecModel] = {}
        self.encoders: Dict[Type, Callable] = {}
        self.decoders: Dict[Type, Callable] = {}

    def load_default_encoders_decoders(self):
        for type_, encoder, decoder in _DEFAULT_ENCODERS_DECODERS:
            self.register_encoder_decoder(type_, encoder, decoder)

    def get_codec_model_key(self, cls, key, value) -> Optional[CodecModelKey]:
        if codec_model := self.get(cls):
            if key not in codec_model:
                codec_model[key] = create_codec_model_key(cls, key, value)
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
                return self[type_].decoder

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
