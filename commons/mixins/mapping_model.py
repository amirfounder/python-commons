_KEY_NOT_SPECIFIED = 'Cannot use "KeyAccessibleMixin" without specifying "key"'
_KEY_INVALID_TYPE = 'Invalid type for key. Expected: <str>. Got: <{}>'
_NO_MATCHING_ATTR = 'Object <{}> has no attribute, "{}". (Defined on inheritance)'


class Mapping:
    def __init_subclass__(cls, **kwargs):
        key = kwargs.get('key')

        if not key:
            raise Exception(_KEY_NOT_SPECIFIED)

        if not isinstance(key, str):
            raise Exception(_KEY_INVALID_TYPE.format(type(key).__name__))

        cls.__key = key

    @property
    def __access_attr(self):
        if hasattr(self, self.__key):
            return getattr(self, self.__key)
        raise Exception(_NO_MATCHING_ATTR.format(type(self).__name__, self.__key))

    def __contains__(self, item):
        return item in self.__access_attr

    def __getitem__(self, item):
        return self.__access_attr[item]

    def __setitem__(self, key, value):
        self.__access_attr[key] = value

    def get(self, key, default=None):
        return self[key] if key in self else default
