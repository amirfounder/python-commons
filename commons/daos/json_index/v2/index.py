from pydantic import BaseModel
from .models import JsonIndexModel


class JsonIndex(BaseModel):
    source: dict[str, JsonIndexModel] = {}

    def __contains__(self, item):
        return item in self.source

    def __getitem__(self, item):
        return self.source[item]

    def __setitem__(self, key, value):
        self.source[key] = value

    def get(self, key, default=None):
        return self.source.get(key, default)
