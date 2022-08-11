from python_commons.helpers.classes import TypeRegistry

def test_type_registry():
    registry = TypeRegistry()

    class Number:
        pass

    class String:
        pass

    registry['number'] = Number

    has_number_key = 'number' in registry
    has_number_cls = Number in registry
    has_string_key = 'string' in registry
    has_string_cls = String in registry

    assert has_number_key is True
    assert has_number_cls is True
    assert has_string_key is False
    assert has_string_cls is False
