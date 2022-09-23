from typing import Type, Any

from commons.logging import log_error

from commons.rest_api.base_model import BaseBLModel
from commons.rest_api.base_dao import BaseDao
from commons.rest_api.http_exceptions import ConflictException, NotFoundException


class BaseResourceValidator:
    dao = None

    def __init__(self, dao: BaseDao):
        self.dao = dao
        self.model_class = dao.db_model_class

    def raise_not_exists(self, filters: dict):
        where_message_parts = [f'{key}={str(value)}' for key, value in filters.items()]
        where_message = ' AND '.join(where_message_parts)

        message = f'Could not find resource {self.model_class.__name__} where: {where_message}.'
        log_error(message)
        raise NotFoundException(message)

    def raise_not_exists_by_field(self, field: str, value: str):
        self.raise_not_exists({field: value})

    def raise_not_exists_by_id(self, resource_id: int):
        self.raise_not_exists({'id': resource_id})

    def raise_resource_id_does_not_match_model(self, resource_id: int, model: BaseBLModel):
        message = f'Resource {self.model_class.__name__} ID {resource_id} does not match provided model ID {model.id}'
        log_error(message)
        raise ConflictException(message)

    def raise_unique_constraint(self, field: str, value: str):
        message = f'Resource {self.model_class.__name__} with {field}={value} already exists.'
        log_error(message)
        raise ConflictException(message)

    def raise_invalid_field_value(self, field: str, value: Any):
        message = f'Invalid value for field {field}: {value}'
        log_error(message)
        raise ConflictException(message)

    def raise_field_does_not_exist(self, field: str):
        message = f'Field {field} does not exist on model {self.model_class.__name__}'
        log_error(message)
        raise ConflictException(message)
    
    def assert_field_exists(self, field: str):
        if not hasattr(self.model_class, field):
            self.raise_field_does_not_exist(field)

    def assert_id_matches_model(self, resource_id, model: BaseBLModel):
        if resource_id != model.id:
            self.raise_resource_id_does_not_match_model(resource_id, model)

    def assert_id_exists(self, resource_id: int):
        if not self.dao.exists_by_id(resource_id):
            self.raise_not_exists({'id': resource_id})

    def validate_resource_is_unique_by_field(self, field: str, value: str):
        if self.dao.exists_by_field(field, value):
            self.raise_unique_constraint(field, value)
