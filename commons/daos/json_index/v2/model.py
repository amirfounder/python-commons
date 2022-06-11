from abc import ABC

from pydantic import BaseModel


class AbstractJsonModel(BaseModel, ABC):
    pass
