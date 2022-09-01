from typing import TypeVar, Generic, Type, Generator, Optional, Dict

from commons.logging import log_warning

from commons.rest_api.pagination import PaginationOptions, PaginatedResults
from commons.rest_api.base_dao import BaseDao
from commons.rest_api.base_model import BaseBLModel
from commons.rest_api.base_resource_validator import BaseResourceValidator

_T = TypeVar('_T', bound=BaseBLModel)


class BaseCRUDService(Generic[_T]):
    resource_bl_model_class: Type[_T]
    resource_dao_class: Type[BaseDao[_T]]
    resource_validator_class: Type[BaseResourceValidator] = BaseResourceValidator

    _cached_resource_validator = None

    @classmethod
    def get_resource_validator(cls) -> BaseResourceValidator:
        if cls._cached_resource_validator is None:
            cls._cached_resource_validator = cls.resource_validator_class(cls.resource_dao_class)
        return cls._cached_resource_validator

    @classmethod
    def get_all(cls, filters: Optional[dict] = None) -> Generator[_T, None, None]:
        return cls.resource_dao_class.get_all(filters=filters)

    @classmethod
    def get_all_paginated(
            cls,
            filters: dict = None,
            pagination_options: PaginationOptions = None,
    ) -> PaginatedResults[_T]:

        offset = pagination_options.size * (pagination_options.page - 1)
        limit = pagination_options.size

        results = cls.resource_dao_class.get_all(filters=filters, offset=offset, limit=limit)
        count = cls.resource_dao_class.count(filters=filters)

        return PaginatedResults(
            results=list(results),
            params=pagination_options.dict(),
            count=count
        )

    @classmethod
    def get_all_by_field(cls, field: str, value: str) -> Generator[_T, None, None]:
        if field not in cls.resource_bl_model_class.__fields__:
            raise ValueError(f'Field {field} is not a valid field for model {cls.resource_bl_model_class.__name__}')

        return cls.get_all(filters={field: value})

    @classmethod
    def get_by_id(cls, resource_id: int, additional_filters: Optional[Dict] = None) -> Optional[_T]:

        model = cls.resource_dao_class.get_by_id(resource_id, additional_filters)

        if not model:
            validation_service = cls.get_resource_validator()
            validation_service.raise_not_exists({'id': resource_id})

        return model

    @classmethod
    def exists(cls, resource_id: int) -> bool:
        return cls.resource_dao_class.exists(resource_id)

    @classmethod
    def create(cls, model: _T) -> _T:
        return cls.resource_dao_class.create(model)

    @classmethod
    def create_many(cls, models: list[_T]) -> Generator[_T, None, None]:
        return cls.resource_dao_class.create_many(models)

    @classmethod
    def update(cls, resource_id: int, model: _T) -> _T:
        resource_validator = cls.get_resource_validator()
        resource_validator.validate_resource_id_matches_model(resource_id, model)
        resource_validator.validate_resource_id_exists(resource_id)

        return cls.resource_dao_class.update(model)

    @classmethod
    def partial_update(cls, resource_id: int, partial_model: dict) -> _T:
        obj_to_update = cls.resource_dao_class.get_by_id_raw(resource_id)

        if not obj_to_update:
            cls.get_resource_validator().raise_not_exists({'id': resource_id})

        for k, v in partial_model.items():
            if k not in obj_to_update:
                log_warning(
                    f'Could not find attribute: {k} in model: {cls.resource_bl_model_class.__name__}. Skipping...')
            else:
                obj_to_update[k] = v

        model_to_update = cls.resource_bl_model_class(**obj_to_update)
        return cls.resource_dao_class.update(model_to_update)

    @classmethod
    def delete(cls, resource_id: int, *, hard: bool = False) -> None:
        model_exists = cls.resource_dao_class.exists(resource_id)

        if not model_exists:
            cls.get_resource_validator().raise_not_exists({'id': resource_id})

        return cls.resource_dao_class.delete(resource_id, hard=hard)
