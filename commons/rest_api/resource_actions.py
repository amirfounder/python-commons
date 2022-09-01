from enum import Enum
from typing import List


class ResourceActions(Enum):
    """
    This is a list of all the actions that can be performed on a resource.
    """
    ALL = 'ALL'
    READ = 'READ'
    UPDATE = 'UPDATE'
    PARTIAL_UPDATE = 'PARTIAL_UPDATE'
    CREATE = 'CREATE'
    SOFT_DELETE = 'SOFT_DELETE'
    HARD_DELETE = 'HARD_DELETE'

    @classmethod
    def all(cls) -> List:
        all_ = list(cls)
        all_.remove(cls.ALL)
        return all_


class SortDirection(Enum):
    ASC = 'ASC'
    DESC = 'DESC'
