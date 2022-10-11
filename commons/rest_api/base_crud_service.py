from typing import TypeVar, Generic, Type, Optional, Any, List

from sqlalchemy.orm import Session

from commons.rest_api.pagination import PaginationOptions, PaginatedResults
from commons.rest_api.base_dao import BaseDao
from commons.rest_api.base_model import BaseBLModel
from commons.rest_api.model_validator import ModelValidator

_T = TypeVar('_T', bound=BaseBLModel)


class BaseCrudService(Generic[_T]):
    def __init__(self, dao: BaseDao, bl_model_class: Type[_T], model_validator_class: Type[ModelValidator] = None):
        self.dao = dao
        self.bl_model_class = bl_model_class
        self.model_validator_class = model_validator_class or ModelValidator

    def _get_offset_limit(self, pagination_options: PaginationOptions) -> (int, int):
        offset = pagination_options.size * (pagination_options.page - 1)
        limit = pagination_options.size

        return offset, limit

    def get_validator(self, *args, **kwargs):
        return self.model_validator_class(*args, **kwargs)

    def _postprocess_model(self, model: _T) -> _T:
        return model

    def _postprocess_models(self, models: List[_T]) -> List[_T]:
        return models

    def _preprocess_model(self, model: _T) -> _T:
        return model

    def _preprocess_models(self, models: List[_T]) -> List[_T]:
        return models

    def get_all(self, filters: dict = None, db_session: Session = None, exclude_fields = None, **kwargs) -> List[_T]:

        models = self.dao.get_all(
            filters=filters or {},
            db_session=db_session,
            exclude_columns=exclude_fields,
            **kwargs
        )
        return self._postprocess_models(models)

    def get_all_paginated(
            self,
            filters: dict = None,
            pagination_options: PaginationOptions = None,
            db_session: Session = None,
            exclude_fields: List[str] = None,
            **kwargs
    ) -> PaginatedResults[_T]:
        
        offset, limit = self._get_offset_limit(pagination_options or PaginationOptions())
        models = self.get_all(
            filters=filters,
            offset=offset,
            limit=limit,
            db_session=db_session,
            exclude_fields=exclude_fields,
            **kwargs
        )

        count = self.dao.count_by_filter(filters=filters)

        return PaginatedResults(
            results=models,
            params=pagination_options.dict(),
            count=count
        )
    
    def get_all_by_field(
            self,
            field: str,
            value: Any,
            db_session: Session = None,
            exclude_fields: List[str] = None
    ) -> List[_T]:

        self.get_validator(self.bl_model_class)\
            .assert_field_exists_on_model(field)\
            .validate()

        results = self.dao.get_all_by_field(field, value, db_session=db_session, exclude_columns=exclude_fields)
        return self._postprocess_models(results)

    def get_all_by_field_paginated(
            self,
            field: str,
            value: Any,
            pagination_options: PaginationOptions = None,
            db_session: Session = None,
            exclude_fields: List[str] = None
    ) -> PaginatedResults[_T]:

        self.get_validator(self.bl_model_class)\
            .assert_field_exists_on_model(field)\
            .validate()

        return self.get_all_paginated(
            filters={field: value},
            pagination_options=pagination_options,
            db_session=db_session,
            exclude_fields=exclude_fields
        )
    
    def get_one_by_field(self, field: str, value: Any, db_session: Session = None, exclude_fields: List[str] = None)\
            -> Optional[_T]:

        result = self.dao.get_one_by_field(field, value, db_session=db_session, exclude_columns=exclude_fields)

        if result is None:
            self.get_validator()\
                .add_model_not_found_by_field_error(field, value)\
                .validate()

        return self._postprocess_model(result)

    def get_by_id(self, resource_id: int, db_session: Session = None, exclude_fields: List[str] = None, **kwargs) \
            -> Optional[_T]:

        model = self.dao.get_by_id(
            resource_id,
            db_session=db_session,
            exclude_columns=exclude_fields,
            **kwargs
        )

        if model is None:
            self.get_validator()\
                .add_model_not_found_by_id_error(resource_id)\
                .validate()

        return self._postprocess_model(model)

    def exists(self, resource_id: int, db_session: Session = None, **kwargs) -> bool:
        return self.dao.exists_by_id(resource_id, db_session=db_session, **kwargs)

    def create(self, model: _T, db_session: Session = None, **kwargs) -> _T:
        model = self._preprocess_model(model)
        model = self.dao.create(model, db_session=db_session, **kwargs)
        return self._postprocess_model(model)

    def create_many(self, models: List[_T], db_session: Session = None, **kwargs) -> List[_T]:
        models = self._preprocess_models(models)
        models = self.dao.create_many(models, db_session=db_session, **kwargs)
        return self._postprocess_models(models)

    def update_by_id(self, resource_id: int, model: _T) -> _T:
        self._preprocess_model(model)

        self.get_validator(model)\
            .assert_resource_id_matches_path_variable_id(resource_id)\
            .validate()

        return self.update(model)

    def update(self, model: _T) -> _T:
        model = self._preprocess_model(model)

        self.get_validator(model)\
            .assert_model_exists_in_db_by_id()\
            .validate()

        model = self.dao.update(model)
        return self._postprocess_model(model)

    def partial_update(self, resource_id: int, partial_model: dict) -> _T:
        model = self.get_by_id(resource_id)

        if not model:
            self.get_validator()\
                .add_model_not_found_by_id_error(resource_id)\
                .validate()

        for key, value in partial_model.items():
            if hasattr(model, key):
                setattr(model, key, value)

        return self.update(model)

    def delete_by_id(self, resource_id: int, db_session: Session, *, hard_delete: bool = False) -> None:
        self.get_validator()\
            .assert_model_exists_in_db_by_id(resource_id)\
            .validate()

        self.dao.delete_by_id(
            resource_id,
            db_session=db_session,
            hard_delete=hard_delete
        )
