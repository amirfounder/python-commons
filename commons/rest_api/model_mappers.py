from typing import Type, Iterable

from pydantic import BaseModel


def map_model(dest_class: Type[BaseModel], model: BaseModel):
    dest_kwargs = model.dict()
    return dest_class(**dest_kwargs)


def map_models(dest_class: Type[BaseModel], models: Iterable[BaseModel]):
    return [map_model(dest_class, model) for model in models]
