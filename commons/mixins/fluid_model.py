class FluidModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, '__slots__') and k not in getattr(self, '__slots__'):
                continue
            setattr(self, k, v)