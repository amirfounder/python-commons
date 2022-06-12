_map = {}


class Builder:
    pass


class Buildable:
    def __init_subclass__(cls, **kwargs):
        _map[cls] = None

    @classmethod
    def builder(cls):
        return _map[cls]

    @classmethod
    def build(cls):
        pass
