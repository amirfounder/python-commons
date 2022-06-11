import json
from abc import ABC
from datetime import datetime
from typing import Callable, Any, Union, Type

from commons.utils import get_attributes
from commons.helpers.datetime import format_iso, parse_iso, now


class DictEncoderMap:
    _encoder_map: dict[type, Callable] = {
        datetime: format_iso,
    }
    _decoder_map: dict[type, dict[str, Callable]] = {
        datetime: parse_iso
    }
    _cls_specific_encoder_map: dict[type, dict[type, Callable]] = {}
    _key_specific_encoder_map: dict[type, dict[type, dict[str, Callable]]] = {}

    @classmethod
    def get_encoder(cls, value_type: Any, klass: type = None, key: str = None) -> Union[Callable, None]:
        return (
            cls._key_specific_encoder_map.get(klass, {}).get(value_type, {}).get(key) or
            cls._cls_specific_encoder_map.get(klass, {}).get(value_type) or
            cls._encoder_map.get(value_type)
        )

    @classmethod
    def get_decoder(cls, klass: Type, key: str) -> Union[Callable, None]:
        return cls._decoder_map.get(klass, {}).get(key)

    @classmethod
    def safe_encode(cls, value, klass: Type = None, key: str = None):
        if encoder := cls.get_encoder(type(value), klass, key):
            return encoder(value)
        return value

    @classmethod
    def safe_decode(cls, value, klass: Type, key: str):
        if decoder := cls.get_decoder(klass, key):
            return decoder(value)
        return value

    @classmethod
    def register_encoder(cls, value_type: Type, encoder: Callable, klass: Type = None, key: str = None):
        if value_type and klass and key:
            cls._key_specific_encoder_map[klass][value_type][key] = encoder
        if value_type and klass and not key:
            cls._cls_specific_encoder_map[klass][value_type] = encoder
        if value_type and not klass and not key:
            cls._encoder_map[value_type] = encoder

    @classmethod
    def register_decoder(cls, klass, key, decoder):
        cls._decoder_map[klass][key] = decoder


class JSONEncodeable(ABC):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __init_subclass__(cls, **kwargs):
        DictEncoderMap.register_encoder(cls, cls.to_dict)

    def to_dict(self):
        obj = {}
        for key, value in get_attributes(self):
            obj[key] = DictEncoderMap.safe_encode(value, type(self), key)
        return obj

    @classmethod
    def from_dict(cls, obj):
        self = cls()
        for key, value in obj.items():
            setattr(self, key, DictEncoderMap.safe_decode(value, cls, key))
        return self

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_obj: str):
        return cls(**json.loads(json_obj))


class Recruiter(JSONEncodeable):
    first_name: str
    last_name: str
    last_contact: datetime
    birthday: datetime


def test_encoding():
    recruiter = Recruiter(
        first_name='Amir',
        last_name='Sharapov',
        birthday=datetime(2000, 3, 9),
        last_contact=now()
    )

    recruiter.to_json()


def test_decoding():
    pass
