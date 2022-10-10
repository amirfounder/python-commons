from typing import TypeVar, Type

_registry = {}
S = TypeVar('S')


def _set_service(class_: S) -> None:
    _registry[class_] = {
        'class': class_,
        'instance': None,
        'initialized': False
    }


def _get_service(class_: Type[S]) -> S:
    if class_ not in _registry:
        _set_service(class_)

    context = _registry[class_]

    if not context['initialized']:
        context['instance'] = context['class']()
        context['initialized'] = True

    _registry[class_] = context

    return context['instance']


def service(class_: S) -> S:
    _set_service(class_)
    return class_


def get_service(class_: Type[S]) -> S:
    return _get_service(class_)


def initialize_services():
    for class_, context in _registry.items():
        if not context['initialized']:
            context['instance'] = context['class']()
            context['initialized'] = True
