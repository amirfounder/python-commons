from typing import Generic, TypeVar, Optional, Type

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel

from commons.logging import log_info
from commons.rest_api.model_mappers import map_models
from commons.rest_api.dtos import BaseDTO
from commons.rest_api.base_model import BaseBLModel

_T = TypeVar('_T', bound=BaseBLModel)


class PaginationOptions(BaseModel):
    _max_page_size = 100

    page: int = 1
    size: int = 20

    @validator('size')
    def validate_page(cls, v):
        if v > cls._max_page_size:
            log_info(
                f'Attempted to retrieve more than {cls._max_page_size} results ({v})... \
                Defaulting to {cls._max_page_size}.'
            )
            v = cls._max_page_size
        return v


class PaginatedResults(GenericModel, Generic[_T]):
    results: Optional[list[_T]]
    params: Optional[dict]
    count: int = 0

    def map_results_to_dtos(self, dto_class: Type[BaseDTO]):
        self.results = map_models(dto_class, self.results)
