from __future__ import annotations
from typing import Iterable, Type, Optional, Set, TypeVar

from pydantic import BaseModel, Extra, create_model

from commons.rest_api.model_mappers import map_model, map_models

_T = TypeVar('_T', bound=BaseModel)


class BaseDTO(BaseModel):
    __bl_model_class__: Type[BaseModel] = None

    class Config:
        extra = Extra.ignore

    @classmethod
    def from_model(cls, model: _T):
        return map_model(cls, model)

    @classmethod
    def from_models(cls, models: Iterable[BaseModel]):
        return map_models(cls, models)

    def to_model(self):
        return map_model(self.__bl_model_class__, self)

    def to_models(self):
        return map_models(self.__bl_model_class__, self)


def generate_dto(
        __model_name,
        resource_bl_model_class: Type[Type[BaseModel]],
        excluded_fields,
        **kwargs
) -> Type[Type[BaseDTO]]:
    kwargs['__base__'] = BaseDTO
    kwargs['__model_name'] = __model_name

    excluded_fields = excluded_fields | kwargs.pop('__excluded_fields__', set())
    child_dto_mappings = kwargs.pop('__child_dto_mappings__', {})

    for k, v in resource_bl_model_class.__fields__.items():
        if k not in excluded_fields:
            if k in child_dto_mappings:
                t_ = child_dto_mappings[k]
            else:
                t_ = v.type_ if v.required else Optional[v.outer_type_]
            kwargs[k] = (t_, (... if v.required else None))

    dto_class = create_model(**kwargs)
    return dto_class


def generate_response_dto(
        __model_name: str,
        resource_bl_model_class: Type[Type[BaseModel]],
        **kwargs
) -> Type[Type[BaseDTO]]:
    dto_class = generate_dto(__model_name, resource_bl_model_class, {'deleted_at'}, **kwargs)
    dto_class.__bl_model_class__ = resource_bl_model_class
    return dto_class


def generate_patch_request_dto(
        __model_name: str,
        resource_bl_model_class: Type[Type[BaseModel]],
        patch_request_fields: Set,
        **kwargs
) -> Type[Type[BaseDTO]]:
    excluded_fields = {'id', 'created_at', 'updated_at', 'deleted_at'}
    for k, v in resource_bl_model_class.__fields__.items():
        if k not in patch_request_fields:
            excluded_fields.add(k)

    dto_class = generate_dto(__model_name, resource_bl_model_class, excluded_fields, **kwargs)
    dto_class.__bl_model_class__ = resource_bl_model_class
    return dto_class


def generate_request_dto(
        __model_name: str,
        resource_bl_model_class: Type[Type[BaseModel]],
        **kwargs
) -> Type[Type[BaseDTO]]:
    excluded_fields = {'id', 'created_at', 'updated_at', 'deleted_at'}
    dto_class = generate_dto(__model_name, resource_bl_model_class, excluded_fields, **kwargs)
    dto_class.__bl_model_class__ = resource_bl_model_class
    return dto_class


def generate_put_request_dto(
        __model_name,
        resource_bl_model_class: Type[Type[BaseModel]],
        **kwargs
) -> Type[Type[BaseDTO]]:
    excluded_fields = {'created_at', 'updated_at', 'deleted_at'}
    dto_class = generate_dto(__model_name, resource_bl_model_class, excluded_fields, **kwargs)
    dto_class.__bl_model_class__ = resource_bl_model_class
    return dto_class
