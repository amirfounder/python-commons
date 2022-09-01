from multipledispatch import dispatch


class TypeRegistry:
    def __init__(self):
        self._cls_map = {}
        self._cls_set = set()

    def __setitem__(self, key, value):
        if key not in self._cls_map:
            self._cls_map[key] = value
            self._cls_set.add(value)

    def __getitem__(self, item):
        if item in self._cls_map:
            return self._cls_map[item]

    @dispatch(type)
    def __contains__(self, item):
        return item in self._cls_set

    @dispatch(str)
    def __contains__(self, item):
        return item in self._cls_map
