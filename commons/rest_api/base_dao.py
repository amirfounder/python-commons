from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Type, Generic, TypeVar, Optional, Iterable, List, Any

from sqlalchemy import update, select, exists, func, delete
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from commons.rest_api.base_model import BaseBLModel, BaseDBModel

_T = TypeVar('_T', bound=BaseBLModel)


class BaseDao(ABC, Generic[_T]):
    bl_model_class: Type[BaseBLModel] = None
    db_model_class: Type[BaseDBModel] = None
    engine: Engine

    def _cast_model(self, model: BaseBLModel | BaseDBModel):
        _m = {
            BaseBLModel: lambda model_: self.db_model_class(**model_.dict()),
            BaseDBModel: lambda model_: self.bl_model_class.from_orm(model_),
        }
        for k, v in _m.items():
            if isinstance(model, k):
                return v(model)
        
        raise Exception("Could not cast model")

    def _create_session(self):
        return Session(self.engine)

    def _apply_filters(self, query, filters: dict):
        for key, value, in filters.items():
            if attr := getattr(self.db_model_class, key, None):
                query = query.where(attr.in_(value) if isinstance(value, list) else attr == value)
        return query

    def _apply_ordering(self, query, ordering: dict):
        for key, value in ordering.items():
            if attr := getattr(self.db_model_class, key, None):
                query = query.order_by(attr.desc() if value == 'desc' else attr.asc())
        return query

    def _apply_offset(self, query, offset: int):
        if offset:
            query = query.offset(offset)
        return query

    def _apply_limit(self, query, limit: int):
        if limit:
            query = query.limit(limit)
        return query

    def _model_has_column(self, key: str) -> bool:
        return self.db_model_class.has_column(key)

    def _assert_model_has_column(self, key: str):
        if not self._model_has_column(key):
            raise ValueError(f'Field {key} does not exist in {self.db_model_class.__name__}')

    def get_all(
            self,
            filters: dict = None,
            db_session: Session = None,
            *,
            offset: int = None,
            limit: int = None,
            order_by: dict = None,
            include_soft_deleted: bool = False,
    ) -> List[_T]:

        order_by = order_by or {'id': 'asc'}

        if db_session is None:
            db_session = self._create_session()

        if not include_soft_deleted:
            filters['deleted_at'] = None

        query = select(self.db_model_class)
        query = self._apply_filters(query, filters or {})
        query = self._apply_offset(query, offset)
        query = self._apply_limit(query, limit)
        query = self._apply_ordering(query, order_by)

        cursor_result = db_session.execute(query)
        results = cursor_result.scalars().all()
        return [self._cast_model(res) for res in results]

    def get_all_by_field(
            self,
            field: str,
            value: Any,
            db_session: Session = None,
            *,
            filters: dict = None,
            offset: int = None,
            limit: int = None,
            order_by: dict = {},
            include_soft_deleted: bool = False,
    ) -> List[_T]:

        self._assert_model_has_column(field)

        filters = filters or {}
        filters[field] = value

        return self.get_all(
            filters=filters,
            db_session=db_session,
            offset=offset,
            limit=limit,
            order_by=order_by,
            include_soft_deleted=include_soft_deleted,
        )

    def get_one_by_field(
            self,
            field: str,
            value: Any,
            db_session: Session = None,
            *,
            filters: dict = None,
            offset: int = None,
            limit: int = None,
            order_by: dict = {},
            include_soft_deleted: bool = False,
    ) -> Optional[_T]:

        results = self.get_all_by_field(
            field,
            value,
            filters=filters,
            db_session=db_session,
            offset=offset,
            limit=limit,
            order_by=order_by,
            include_soft_deleted=include_soft_deleted,
        )

        return next(iter(results), None)

    def get_by_id(
            self,
            model_id: int,
            db_session: Session = None,
            filters: dict = None,
            *,
            include_soft_deleted: bool = False,
    ) -> Optional[_T]:

        return self.get_one_by_field(
            'id',
            model_id,
            db_session=db_session,
            filters=filters,
            include_soft_deleted=include_soft_deleted,
        )

    def create(self, model: _T, db_session: Session = None, *, commit: bool = True) -> _T:

        if db_session is None:
            db_session = self._create_session()

        db_model = self._cast_model(model)
        db_session.add(db_model)

        if commit:
            db_session.commit()

        return self._cast_model(db_model)

    def create_many(self, models: Iterable[_T], db_session: Session = None, *, commit: bool = True) -> List[_T]:

        if db_session is None:
            db_session = self._create_session()

        db_models = [self._cast_model(model) for model in models]
        db_session.add_all(db_models)

        if commit:
            db_session.commit()

        return [self._cast_model(db_model) for db_model in db_models]

    def update(self, model: _T, db_session: Session = None, *, commit: bool = True) -> _T:

        if db_session is None:
            db_session = self._create_session()

        db_model = self._cast_model(model)
        db_session.merge(db_model)

        if commit:
            db_session.commit()

        return self._cast_model(db_model)

    def delete(self, model: _T, db_session: Session = None, *, commit: bool = True, hard_delete: bool = False) -> None:
        if hard_delete:
            self.hard_delete(model, db_session=db_session, commit=commit)
        else:
            self.soft_delete(model, db_session=db_session, commit=commit)

    def hard_delete(self, model: _T, db_session: Session = None, *, commit: bool = True) -> None:

        if db_session is None:
            db_session = self._create_session()

        db_model = self._cast_model(model)
        db_session.delete(db_model)

        if commit:
            db_session.commit()

    def soft_delete(self, model: _T, db_session: Session = None, *, commit: bool = True) -> None:

        if db_session is None:
            db_session = self._create_session()

        model.deleted_at = datetime.utcnow()
        self.update(model, db_session=db_session, commit=commit)

    def delete_by_id(
            self,
            model_id: int,
            db_session: Session = None,
            *,
            commit: bool = True,
            hard_delete: bool = False
    ) -> None:

        if hard_delete:
            self.hard_delete_by_id(model_id, db_session=db_session, commit=commit)
        else:
            self.soft_delete_by_id(model_id, db_session=db_session, commit=commit)

    def hard_delete_by_id(self, model_id: int, db_session: Session = None, *, commit: bool = True) -> None:
        query = (
            delete(self.db_model_class)
            .where(self.db_model_class.id == model_id)
        )
        db_session.execute(query)
        if commit:
            db_session.commit()

    def soft_delete_by_id(self, model_id: int, db_session: Session = None, *, commit: bool = True) -> None:
        query = (
            update(self.db_model_class)
            .where(self.db_model_class.id == model_id)
            .values(deleted_at=datetime.utcnow())
        )
        db_session.execute(query)
        if commit:
            db_session.commit()

    def count_by_filter(
            self,
            filters: dict = None,
            db_session: Session = None,
            *,
            include_soft_deleted: bool = False,
    ) -> int:
        filters = filters or {}

        if db_session is None:
            db_session = self._create_session()

        if not include_soft_deleted:
            filters['deleted_at'] = None

        query = select(func.count(self.db_model_class.id))
        query = self._apply_filters(query, filters)

        cursor_result = db_session.execute(query)
        return cursor_result.scalar()

    def exists_by_filter(
            self,
            filters: dict = None,
            db_session: Session = None,
            *,
            include_soft_deleted: bool = False
    ) -> bool:
        filters = filters or {}

        if db_session is None:
            db_session = self._create_session()

        if not include_soft_deleted:
            filters['deleted_at'] = None

        query = select(self.db_model_class)
        query = self._apply_filters(query, filters)
        query = select(exists(query))

        cursor_result = db_session.execute(query)
        return cursor_result.scalar().first() is not None

    def exists_by_field(
            self,
            field: str,
            value: Any,
            db_session: Session = None,
            *,
            include_soft_deleted: bool = False
    ) -> bool:
        return self.exists_by_filter(
            {field: value},
            db_session=db_session,
            include_soft_deleted=include_soft_deleted,
        )

    def exists_by_id(self, model_id: int, db_session: Session = None, *, include_soft_deleted: bool = False) -> bool:
        return self.exists_by_field(
            'id',
            model_id,
            db_session=db_session,
            include_soft_deleted=include_soft_deleted,
        )
