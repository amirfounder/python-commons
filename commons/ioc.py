_registry = {}

def get_registry():
    global _registry
    return _registry


def service(class_):
    global _registry
    _registry[class_] = class_()
    return class_


def get_service(class_):
    global _registry
    return _registry[class_]
