from enum import Enum


class AllMixin(Enum):
    @classmethod
    def all(cls):
        all_ = list(cls)
        if hasattr(cls, 'ALL'):
            all_.remove(cls.ALL)
        return all_
