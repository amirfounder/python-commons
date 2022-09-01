from enum import Enum


class AllMixin(Enum):
    ALL = 'ALL'

    @classmethod
    def all(cls):
        all_ = list(cls)
        all_.remove(cls.ALL)
        return all_
