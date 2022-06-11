from typing import TypeVar, Optional, Any, Generic

_KEY_NOT_SPECIFIED = 'Cannot use "KeyAccessibleMixin" without specifying "key"'
_KEY_INVALID_TYPE = 'Invalid type for key. Expected: <str>. Got: <{}>'
_NO_MATCHING_ATTR = 'Object <{}> has no attribute, "{}". (Defined on inheritance)'


_K = TypeVar('_K', bound=Any)
_V = TypeVar('_V', bound=Any)


class Mapping(Generic[_K, _V]):
    def __init_subclass__(cls, key='source', **kwargs):
        if not isinstance(key, str):
            raise Exception(_KEY_INVALID_TYPE.format(type(key).__name__))
        cls.__key = key

    @property
    def __source(self):
        if hasattr(self, self.__key):
            return getattr(self, self.__key)
        raise Exception(_NO_MATCHING_ATTR.format(type(self).__name__, self.__key))

    def __contains__(self, item) -> bool:
        return item in self.__source

    def __getitem__(self, item) -> _V:
        return self.__source[item]

    def __setitem__(self, key, value) -> None:
        self.__source[key] = value

    def get(self, key, default=None) -> Optional[_V]:
        return self[key] if key in self else default
