_registry = {}

def get_registry():
    global _registry
    return _registry


def service(class_):
    def wrapper(*args, **kwargs):
        global _registry
        _registry[class_] = class_(*args, **kwargs)
        return class_
    return wrapper


def get_service(class_):
    global _registry
    return _registry[class_]
