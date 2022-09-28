from __future__ import annotations
from typing import Any, Optional, Callable, Type, Union

from sqlalchemy.orm import Session

from commons.logging import log_error, log_warning
from commons.rest_api.base_model import BaseBLModel
from commons.rest_api.base_dao import BaseDao
from commons.rest_api.http_exceptions import BadRequestException, InternalServerErrorException


class ValidationError:
    def __init__(self, message: str, err_status_code: int = 400):
        self.message = message
        self.status_code = err_status_code


class ModelNotFoundByFilterError(ValidationError):
    def __init__(self, params: dict[str, Any], err_status_code: int = 404):
        message = "Could not find record where "
        for key, value in params.items():
            message += f"{key} = {value} and "
        message = message[:-5] + "."

        super().__init__(message, err_status_code)


class ModelAlreadyExistsError(ValidationError):
    def __init__(self, params: dict[str, Any], err_status_code: int = 409):
        message = "Record already exists where "
        for key, value in params.items():
            message += f"{key} = {value} and "
        message = message[:-5] + "."

        super().__init__(message, err_status_code)


class InvalidValueForFieldError(ValidationError):
    def __init__(self, field_name: str, value: Any, err_status_code: int = 400):
        message = f"Invalid value for field {field_name}: {value}"
        super().__init__(message, err_status_code)


class ModelValidator:
    def __init__(self, model: Union[BaseBLModel | Type[BaseBLModel]] = None, dao: BaseDao = None, *, db_session: Session = None):
        self.model = model
        self.model_dict = model.dict() if model else None
        self.db_session = db_session
        self.dao = dao
        self._validators = []

    def _add_validator(self, validator: callable, is_custom: bool = False):
        self._validators.append({
            'validator': validator,
            'is_custom': is_custom
        })

    def _build_validator_context(self):
        return {'builder': self}

    def _ensure_dao_exists(self):
        if not self.dao:
            log_warning('No DAO provided for model validation. Skipping validation step.')
            return False
        return True
    
    def _ensure_model_exists(self):
        if not self.model:
            log_error('No model provided for validation. Skipping validation step.')
            raise InternalServerErrorException('No model provided for validation. Skipping validation step.')
        return True

    def add_custom_validation_error(self, error: ValidationError):
        self._add_validator(lambda: error)
        return self

    def add_model_not_found_by_filter_error(self, params: dict[str, Any], *, on_fail_status_code: int = 404):
        error = ModelNotFoundByFilterError(params, on_fail_status_code)
        self.add_custom_validation_error(error)
        return self
    
    def add_model_not_found_by_field_error(self, field: str, value: Any, *, on_fail_status_code: int = 404):
        error = ModelNotFoundByFilterError({field: value}, on_fail_status_code)
        self.add_custom_validation_error(error)
        return self
    
    def add_model_not_found_by_id_error(self, resource_id: int, *, on_fail_status_code: int = 404):
        error = ModelNotFoundByFilterError({'id': resource_id}, on_fail_status_code)
        self.add_custom_validation_error(error)
        return self

    def assert_custom_validation(self, validator: Callable[[dict], Optional[ValidationError]]):
        self._add_validator(validator, is_custom=True)
        return self

    def assert_resource_id_matches_path_variable_id(
            self,
            path_variable_id: int,
            model: Type[BaseBLModel] | BaseBLModel = None,
            *,
            on_fail_status_code: int = 400,
    ):
        model = model or self.model

        def validator():
            if model.id != path_variable_id:
                return ValidationError(
                    f"Model ID {model.id} does not match path variable ID {path_variable_id}",
                    on_fail_status_code
                )

        self._add_validator(validator)
        return self

    def assert_field_exists_on_model(
            self,
            field: str,
            model: Type[BaseBLModel] | BaseBLModel = None,
            *,
            on_fail_status_code: int = 400
    ):
        model = model or self.model

        def validator():
            if field not in model.__fields__:
                return ValidationError(f"Field {field} does not exist on model", on_fail_status_code)

        self._add_validator(validator)
        return self

    def assert_field_is_not_null_on_model(
            self,
            field_name: str,
            model: Type[BaseBLModel] | BaseBLModel = None,
            *,
            on_fail_status_code: int = 400
    ):
        model = model or self.model

        def validator():
            if field_name not in model.__fields__:
                return ValidationError(f"Field {field_name} does not exist on model", on_fail_status_code)

            if model.dict()[field_name] is None:
                return ValidationError(f"Field {field_name} is empty", on_fail_status_code)

        self._add_validator(validator)
        return self

    def assert_models_do_not_exist_in_db_by_field(
            self,
            field: str,
            value: Any = None,
            *,
            on_fail_status_code: int = 409
    ):
        value = value or self.model_dict[field]

        if not self._ensure_dao_exists():
            return self

        def validator():
            if self.dao.exists_by_field(field, value):
                return ModelAlreadyExistsError({field: value}, on_fail_status_code)

        self._add_validator(validator)
        return self

    def assert_models_do_not_exist_in_db_by_filter(self, params: dict[str, Any], *, on_fail_status_code: int = 409):
        if not self._ensure_dao_exists():
            return self

        def validator():
            if self.dao.exists_by_filter(params):
                return ModelAlreadyExistsError(params, on_fail_status_code)

        self._add_validator(validator)
        return self

    def assert_models_do_not_exist_in_db_by_id(self, resource_id: int = None, *, on_fail_status_code: int = 409):
        resource_id = resource_id or self.model.id

        if not self._ensure_dao_exists():
            return self

        def validator():
            if self.dao.exists_by_id(resource_id):
                return ModelAlreadyExistsError({'id': resource_id}, on_fail_status_code)

        self._add_validator(validator)
        return self

    def assert_model_exists_in_db_by_field(self, field: str, value: Any = None, *, on_fail_status_code: int = 404):
        value = value or self.model_dict[field]

        if not self._ensure_dao_exists():
            return self

        def validator():
            if not self.dao.exists_by_field(field, value):
                return ModelNotFoundByFilterError({field: value}, on_fail_status_code)

        self._add_validator(validator)
        return self

    def assert_model_exists_in_db_by_filter(self, params: dict[str, Any], *, on_fail_status_code: int = 404):
        if not self._ensure_dao_exists():
            return self

        def validator():
            if not self.dao.exists_by_filter(params):
                return ModelNotFoundByFilterError(params, on_fail_status_code)

        self._add_validator(validator)
        return self

    def assert_model_exists_in_db_by_id(self, resource_id: int = None, *, on_fail_status_code: int = 404):
        resource_id = resource_id or self.model.id

        if not self._ensure_dao_exists():
            return self

        def validator():
            if not self.dao.exists_by_id(resource_id):
                return ModelNotFoundByFilterError({'id': resource_id}, on_fail_status_code)

        self._add_validator(validator)
        return self

    def validate(self):
        error_messages = []

        for validator in self._validators:
            if validator['is_custom']:
                ctx = self._build_validator_context()
                error = validator['validator'](ctx)
            else:
                error = validator['validator']()

            if error:
                error_messages.append(error.message)

        if len(error_messages) > 0:
            message = f'Validation failed: [{", ".join(error_messages)}]'
            log_error(message)
            raise BadRequestException(message)
