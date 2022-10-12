from __future__ import annotations

from abc import ABC
from datetime import datetime
from typing import Type, Generic, TypeVar, Optional, Iterable, List, Any, Dict

from sqlalchemy import update, select, exists, func, delete
from sqlalchemy.engine import Engine, Row
from sqlalchemy.orm import Session, InstrumentedAttribute

from commons.rest_api.base_model import BaseBLModel, BaseDBModel

_T = TypeVar('_T', bound=BaseBLModel)


class BaseDao(ABC, Generic[_T]):
    bl_model_class: Type[BaseBLModel] = None
    db_model_class: Type[BaseDBModel] = None
    engine: Engine

    def __init__(
            self,
            *,
            bl_model_class: Type[BaseBLModel] = None,
            db_model_class: Type[BaseDBModel] = None,
            engine: Engine = None
    ):
        self.bl_model_class = bl_model_class or self.bl_model_class
        self.db_model_class = db_model_class or self.db_model_class
        self.engine = engine or self.engine

    def _cast_to_bl_model(self, model: BaseDBModel | Dict | Row, bl_model_class: Type[BaseBLModel] = None) -> _T:
        bl_model_class = bl_model_class or self.bl_model_class

        if isinstance(model, Row):
            model = self.db_model_class(**model)

        if isinstance(model, self.db_model_class):
            return bl_model_class.from_orm(model)

        return bl_model_class(**model)

    def _cast_to_db_model(self, model: BaseBLModel, db_model_class: Type[BaseDBModel] = None) -> BaseDBModel:
        db_model_class = db_model_class or self.db_model_class
        return db_model_class(**model.dict())

    def _create_session(self):
        return Session(self.engine)

    def _create_select_query(self, *, exclude_columns: List[str | InstrumentedAttribute] = None) -> select:
        exclude_columns = exclude_columns or []
        exclude_columns = set(exclude_columns)

        attributes = self.db_model_class.get_instrumented_attributes(
            filters=[
                lambda attr: attr.is_selectable,
                lambda attr: attr not in exclude_columns and attr.key not in exclude_columns,
            ]
        )
        return select(*attributes)

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
            close_db_session: bool = False,
            *,
            offset: int = None,
            limit: int = None,
            order_by: dict = None,
            include_soft_deleted: bool = False,
            exclude_columns: List[str] = None,
            bl_model_class: Type[BaseBLModel] = None,
    ) -> List[_T]:

        bl_model_class = bl_model_class or self.bl_model_class
        filters = filters or {}
        order_by = order_by or {'id': 'asc'}

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        if not include_soft_deleted:
            filters['deleted_at'] = None

        query = self._create_select_query(exclude_columns=exclude_columns)
        query = self._apply_filters(query, filters or {})
        query = self._apply_offset(query, offset)
        query = self._apply_limit(query, limit)
        query = self._apply_ordering(query, order_by)

        cursor_result = db_session.execute(query)
        results = [self._cast_to_bl_model(row, bl_model_class) for row in cursor_result]

        if close_db_session:
            db_session.close()

        return results

    def get_all_by_field(
            self,
            field: str,
            value: Any,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            filters: dict = None,
            offset: int = None,
            limit: int = None,
            order_by: dict = {},
            include_soft_deleted: bool = False,
            exclude_columns: List[str] = None,
            bl_model_class: Type[BaseBLModel] = None,
    ) -> List[_T]:

        self._assert_model_has_column(field)

        filters = filters or {}
        filters[field] = value

        return self.get_all(
            filters=filters,
            db_session=db_session,
            close_db_session=close_db_session,
            offset=offset,
            limit=limit,
            order_by=order_by,
            include_soft_deleted=include_soft_deleted,
            exclude_columns=exclude_columns,
            bl_model_class=bl_model_class,
        )

    def get_one_by_field(
            self,
            field: str,
            value: Any,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            filters: dict = None,
            order_by: dict = {},
            include_soft_deleted: bool = False,
            exclude_columns: List[str] = None,
            bl_model_class: Type[BaseBLModel] = None,
    ) -> Optional[_T]:

        results = self.get_all_by_field(
            field,
            value,
            filters=filters,
            db_session=db_session,
            close_db_session=close_db_session,
            offset=0,
            limit=1,
            order_by=order_by,
            include_soft_deleted=include_soft_deleted,
            exclude_columns=exclude_columns,
            bl_model_class=bl_model_class,
        )

        return next(iter(results), None)

    def get_by_id(
            self,
            resource_id: int,
            db_session: Session = None,
            close_db_session: bool = False,
            filters: dict = None,
            *,
            include_soft_deleted: bool = False,
            exclude_columns: List[str] = None,
            bl_model_class: Type[BaseBLModel] = None,
    ) -> Optional[_T]:

        return self.get_one_by_field(
            'id',
            resource_id,
            db_session=db_session,
            close_db_session=close_db_session,
            filters=filters,
            include_soft_deleted=include_soft_deleted,
            exclude_columns=exclude_columns,
            bl_model_class=bl_model_class,
        )

    def create(
            self,
            model: _T,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            commit: bool = True
    ) -> _T:

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        db_model = self._cast_to_db_model(model)
        db_session.add(db_model)

        if commit:
            db_session.commit()

        result = self._cast_to_bl_model(db_model)

        if close_db_session:
            db_session.close()

        return result

    def create_many(
            self,
            models: Iterable[_T],
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            commit: bool = True
    ) -> List[_T]:

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        db_models = [self._cast_to_db_model(model) for model in models]
        db_session.add_all(db_models)

        if commit:
            db_session.commit()

        results = [self._cast_to_bl_model(db_model) for db_model in db_models]

        if close_db_session:
            db_session.close()

        return results

    def update(
            self,
            model: _T,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            commit: bool = True
    ) -> _T:

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        db_model = self._cast_to_db_model(model)
        db_session.merge(db_model)

        if commit:
            db_session.commit()

        result = self._cast_to_bl_model(db_model)

        if close_db_session:
            db_session.close()

        return result

    def delete(
            self,
            model: _T,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            commit: bool = True,
            hard_delete: bool = False
    ) -> None:

        kwargs = {
            'model': model,
            'db_session': db_session,
            'close_db_session': close_db_session,
            'commit': commit,
        }

        if hard_delete:
            return self.hard_delete(**kwargs)

        return self.soft_delete(**kwargs)

    def hard_delete(
            self,
            model: _T,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            commit: bool = True
    ) -> None:

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        db_model = self._cast_to_db_model(model)
        db_session.delete(db_model)

        if commit:
            db_session.commit()

        if close_db_session:
            db_session.close()

    def soft_delete(
            self,
            model: _T,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            commit: bool = True
    ) -> None:

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        model.deleted_at = datetime.utcnow()
        self.update(model, db_session=db_session, close_db_session=close_db_session, commit=commit)

    def delete_by_id(
            self,
            resource_id: int,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            commit: bool = True,
            hard_delete: bool = False
    ) -> None:

        kwargs = {
            'resource_id': resource_id,
            'db_session': db_session,
            'close_db_session': close_db_session,
            'commit': commit,
        }

        if hard_delete:
            return self.hard_delete_by_id(**kwargs)

        return self.soft_delete_by_id(**kwargs)

    def hard_delete_by_id(
            self,
            resource_id: int,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            commit: bool = True
    ) -> None:
        query = (
            delete(self.db_model_class)
            .where(self.db_model_class.id == resource_id)
        )

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        db_session.execute(query)

        if commit:
            db_session.commit()

        if close_db_session:
            db_session.close()

    def soft_delete_by_id(
            self,
            resource_id: int,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            commit: bool = True
    ) -> None:

        query = (
            update(self.db_model_class)
            .where(self.db_model_class.id == resource_id)
            .values(deleted_at=datetime.utcnow())
        )

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        db_session.execute(query)

        if commit:
            db_session.commit()

        if close_db_session:
            db_session.close()

    def count_by_filter(
            self,
            filters: dict = None,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            include_soft_deleted: bool = False,
    ) -> int:
        filters = filters or {}

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        if not include_soft_deleted:
            filters['deleted_at'] = None

        query = select(func.count(self.db_model_class.id))
        query = self._apply_filters(query, filters)

        cursor_result = db_session.execute(query)
        result = cursor_result.scalar()

        if close_db_session:
            db_session.close()

        return result

    def exists_by_filter(
            self,
            filters: dict = None,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            include_soft_deleted: bool = False
    ) -> bool:
        filters = filters or {}

        if db_session is None:
            db_session = self._create_session()
            close_db_session = True

        if not include_soft_deleted:
            filters['deleted_at'] = None

        query = select(self.db_model_class)
        query = self._apply_filters(query, filters)
        query = select(exists(query))

        cursor_result = db_session.execute(query)
        result = cursor_result.scalar()

        if close_db_session:
            db_session.close()

        return result

    def exists_by_field(
            self,
            field: str,
            value: Any,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            include_soft_deleted: bool = False
    ) -> bool:
        return self.exists_by_filter(
            {field: value},
            db_session=db_session,
            close_db_session=close_db_session,
            include_soft_deleted=include_soft_deleted,
        )

    def exists_by_id(
            self,
            resource_id: int,
            db_session: Session = None,
            close_db_session: bool = False,
            *,
            include_soft_deleted: bool = False
    ) -> bool:
        return self.exists_by_field(
            'id',
            resource_id,
            db_session=db_session,
            close_db_session=close_db_session,
            include_soft_deleted=include_soft_deleted,
        )
