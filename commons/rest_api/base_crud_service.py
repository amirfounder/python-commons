from typing import TypeVar, Generic, Type, Generator, Optional, Dict, Any, List

from sqlalchemy.orm import Session

from commons.logging import log_warning

from commons.rest_api.pagination import PaginationOptions, PaginatedResults
from commons.rest_api.base_dao import BaseDao
from commons.rest_api.base_model import BaseBLModel
from commons.rest_api.base_resource_validator import ModelValidator

_T = TypeVar('_T', bound=BaseBLModel)


class BaseCrudService(Generic[_T]):
    def __init__(self, dao: BaseDao, validator: ModelValidator = None):
        self.dao = dao
        self.validator = validator or ModelValidator(dao)

    def get_all(self, filters: dict = None, db_session: Session = None, **kwargs) -> List[_T]:
        return self.dao.get_all(
            filters=filters or {},
            db_session=db_session,
            **kwargs
        )
    
    def get_all_paginated(
            self,
            filters: dict = None,
            pagination_options: PaginationOptions = None,
            db_session: Session = None,
            **kwargs
    ) -> PaginatedResults[_T]:
        
        offset = pagination_options.size * (pagination_options.page - 1)
        limit = pagination_options.size

        results = self.get_all(filters=filters, offset=offset, limit=limit, db_session=db_session, **kwargs)
        count = self.dao.count_by_filter(filters=filters)

        return PaginatedResults(
            results=results,
            params=pagination_options.dict(),
            count=count
        )
    
    def get_all_by_field(self, field: str, value: Any, db_session: Session = None) -> List[_T]:
        self.validator.assert_field_exists(field)
        return self.dao.get_all_by_field(field, value, db_session=db_session)

    def get_all_by_field_paginated(
            self,
            field: str,
            value: Any,
            pagination_options: PaginationOptions = None,
            db_session: Session = None
    ) -> PaginatedResults[_T]:
        self.validator.assert_field_exists(field)
        return self.get_all_paginated(
            filters={field: value},
            pagination_options=pagination_options,
            db_session=db_session
        )
    
    def get_one_by_field(self, field: str, value: Any, db_session: Session = None) -> Optional[_T]:
        res = self.dao.get_one_by_field(field, value, db_session=db_session)

        if res is None:
            validator = self.validator
            validator.raise_not_exists_by_field(field, value)

        return res

    def get_by_id(self, model_id: int, db_session: Session = None, **kwargs) -> Optional[_T]:
        res = self.dao.get_by_id(model_id, db_session=db_session, **kwargs)

        if res is None:
            self.validator.raise_not_exists_by_id(model_id)

        return res

    def exists(self, resource_id: int, db_session: Session = None, **kwargs) -> bool:
        return self.dao.exists_by_id(resource_id, db_session=db_session, **kwargs)

    def create(cls, model: _T, db_session: Session = None, **kwargs) -> _T:
        return cls.dao.create(model, db_session=db_session, **kwargs)

    def create_many(self, models: List[_T], db_session: Session = None, **kwargs) -> List[_T]:
        return self.dao.create_many(models, db_session=db_session, **kwargs)

    def update_by_id(self, resource_id: int, model: _T) -> _T:
        self.validator.assert_id_matches_model(resource_id, model)
        return self.update(model)

    def update(self, model: _T) -> _T:
        self.validator.assert_id_exists(model.id)
        return self.dao.update(model)

    def partial_update(self, resource_id: int, partial_model: dict) -> _T:
        model = self.get_by_id(resource_id)

        if not model:
            self.validator.raise_not_exists_by_id(resource_id)

        for key, value in partial_model.items():
            if hasattr(model, key):
                setattr(model, key, value)

        return self.update(model)

    def delete_by_id(self, resource_id: int, db_session: Session, *, hard_delete: bool = False) -> None:
        self.validator.assert_id_exists(resource_id)
        self.dao.delete_by_id(
            resource_id,
            db_session=db_session,
            hard_delete=hard_delete
        )
