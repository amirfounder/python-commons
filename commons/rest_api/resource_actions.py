from enum import Enum

from commons.enums import AllMixin


class ResourceActions(Enum, AllMixin):
    """
    This is a list of all the actions that can be performed on a resource.
    """
    READ = 'READ'
    UPDATE = 'UPDATE'
    PARTIAL_UPDATE = 'PARTIAL_UPDATE'
    CREATE = 'CREATE'
    SOFT_DELETE = 'SOFT_DELETE'
    HARD_DELETE = 'HARD_DELETE'


class SortDirection(Enum):
    ASC = 'ASC'
    DESC = 'DESC'
