from typing import Type, Iterable, TypeVar, List

from pydantic import BaseModel

_T = TypeVar('T', bound=BaseModel)


def map_model(dest_class: Type[_T], model: BaseModel) -> _T:
    dest_kwargs = model.dict()
    return dest_class(**dest_kwargs)


def map_models(dest_class: Type[_T], models: Iterable[BaseModel]) -> List[_T]:
    return [map_model(dest_class, model) for model in models]
