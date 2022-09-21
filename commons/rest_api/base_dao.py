from __future__ import annotations

from typing import Type, Generic, TypeVar, Optional, Iterable, Generator, Dict, List, Any

from commons.datetime import now
from sqlalchemy import insert, update, select, exists, func, delete
from sqlalchemy.engine import CursorResult, Engine
from sqlalchemy.orm import DeclarativeMeta

from commons.rest_api.base_model import BaseBLModel

_T = TypeVar('_T', bound=BaseBLModel)


class BaseDao(Generic[_T]):
    resource_bl_model_class: Type[_T]
    resource_db_model_class: Type[Type[DeclarativeMeta]]
    engine: Engine

    @classmethod
    def _model_to_obj(cls, model: _T) -> Dict:
        return model.dict()

    @classmethod
    def _obj_to_model(cls, obj: Dict) -> _T:
        return cls.resource_bl_model_class(**obj)

    @classmethod
    def _objs_to_models(cls, objs: List[Dict]) -> List[_T]:
        return [cls._obj_to_model(obj) for obj in objs]

    @classmethod
    def _models_to_objs(cls, models: List[_T]) -> List[Dict]:
        return [cls._model_to_obj(model) for model in models]

    @classmethod
    def _prepare_for_create(cls, obj: dict):
        now_ = now()
        obj.pop('id', None)
        obj['created_at'] = now_
        obj['updated_at'] = now_

    @classmethod
    def _prepare_for_update(cls, obj: dict):
        obj['updated_at'] = now()

    @classmethod
    def _apply_filters_to_query(cls, query, filters: dict):
        filter_clauses = []
        for k, v in filters.items():
            if attr := getattr(cls.resource_db_model_class, k, None):
                filter_clauses.append((attr, v))

        for attr, value in filter_clauses:
            is_value_list = isinstance(value, list)
            clause = attr.in_(value) if is_value_list else attr == value
            query = query.where(clause)

        return query

    @classmethod
    def _apply_offset_limit_to_query(cls, query, offset: int = None, limit: int = None):
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        return query

    @classmethod
    def get_all_raw(cls, filters: dict = None, **kwargs) -> Generator[dict, None, None]:
        if filters is None:
            filters = {}

        query = select(cls.resource_db_model_class)
        query = cls._apply_filters_to_query(query, filters)
        query = cls._apply_offset_limit_to_query(query, kwargs.get('offset'), kwargs.get('limit'))
        query = query.order_by(cls.resource_db_model_class.id.asc())

        with cls.engine.connect() as conn:
            result: CursorResult = conn.execute(query)
            conn.commit()

        for row in result:
            obj = dict(row)
            yield obj

    @classmethod
    def get_all(cls, filters: dict = None, **kwargs) -> Generator[_T, None, None]:
        objs = cls.get_all_raw(filters=filters, **kwargs)
        for obj in objs:
            yield cls._obj_to_model(obj)

    @classmethod
    def get_by_id_raw(cls, resource_id: int, additional_filters: Optional[dict] = None) -> Optional[dict]:
        filters = {
            'id': resource_id,
            'deleted_at': None
        }

        if additional_filters:
            filters.update(additional_filters)

        models = cls.get_all_raw(filters)
        return next(models, None)

    @classmethod
    def get_by_id(cls, resource_id: int, additional_filters: Optional[dict] = None) -> Optional[_T]:
        if obj := cls.get_by_id_raw(resource_id, additional_filters):
            return cls._obj_to_model(obj)

    @classmethod
    def get_all_by_field_raw(cls):
        pass

    @classmethod
    def get_all_by_field(cls):
        pass

    @classmethod
    def get_one_by_field_raw(cls):
        pass

    @classmethod
    def get_one_by_field(cls):
        pass

    @classmethod
    def create_raw(cls, obj: dict) -> dict:
        cls._prepare_for_create(obj)
        cls.resource_db_model_class.clean_obj(obj)

        query = insert(cls.resource_db_model_class).values(**obj)

        with cls.engine.connect() as conn:
            result = conn.execute(query)
            conn.commit()

        obj['id'] = result.inserted_primary_key[0]
        return obj

    @classmethod
    def create(cls, model: _T) -> _T:
        obj = cls._model_to_obj(model)
        obj = cls.create_raw(obj)
        return cls._obj_to_model(obj)

    @classmethod
    def create_many_raw(cls, objs: Iterable[dict]) -> Generator[dict, None, None]:
        for obj in objs:
            cls._prepare_for_create(obj)

        with cls.engine.connect() as conn:
            for obj in objs:
                cls.resource_db_model_class.clean_obj(obj)
                query = insert(cls.resource_db_model_class).values(**obj)
                result = conn.execute(query)
                obj['id'] = result.inserted_primary_key[0]

            conn.commit()

        for obj in objs:
            yield obj

    @classmethod
    def create_many(cls, models: List[_T]) -> Generator[_T, None, None]:
        objs = cls._models_to_objs(models)
        objs = cls.create_many_raw(objs)
        for obj in objs:
            yield cls._obj_to_model(obj)

    @classmethod
    def update_raw(cls, obj: Dict) -> Dict:
        cls._prepare_for_update(obj)
        cls.resource_db_model_class.clean_obj(obj)

        query = update(cls.resource_db_model_class).values(**obj)
        query = query.where(cls.resource_db_model_class.id == obj['id'])

        with cls.engine.connect() as conn:
            conn.execute(query)
            conn.commit()

        return obj

    @classmethod
    def update(cls, model: _T) -> _T:
        obj = cls._model_to_obj(model)
        obj = cls.update_raw(obj)
        return cls._obj_to_model(obj)

    @classmethod
    def exists(cls, resource_id: int):
        return cls.exists_by_field('id', resource_id)

    @classmethod
    def exists_by_field(cls, field: str, value: Any):
        return cls.exists_by_filter({field: value})

    @classmethod
    def exists_by_filter(cls, filters: dict):
        with cls.engine.connect() as conn:
            query = select(cls.resource_db_model_class)
            query = cls._apply_filters_to_query(query, filters)
            query = select(exists(query))

            result = conn.execute(query)
            conn.commit()

        return result.scalar()

    @classmethod
    def count(cls, filters: dict = None) -> int:
        if filters is None:
            filters = {}

        query = select(func.count(cls.resource_db_model_class.id))
        query = cls._apply_filters_to_query(query, filters)

        with cls.engine.connect() as conn:
            result = conn.execute(query)
            conn.commit()

        return result.scalar()

    @classmethod
    def delete(cls, resource_id: int, *, hard: bool = False) -> None:
        if hard:
            return cls.hard_delete(resource_id)
        return cls.soft_delete(resource_id)

    @classmethod
    def soft_delete(cls, resource_id: int):
        model: _T = cls.get_by_id(resource_id)

        if not model:
            return

        model.deleted_at = now()
        cls.update(model)

    @classmethod
    def hard_delete(cls, resource_id: int):
        with cls.engine.connect() as conn:
            query = delete(cls.resource_db_model_class).where(cls.resource_db_model_class.id == resource_id)
            conn.execute(query)
            conn.commit()
