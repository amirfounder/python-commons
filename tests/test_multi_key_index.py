from unittest import TestCase

from commons.multi_key_index import MultiKeyIndex

class TestMultiIndexCache(TestCase):
    def _setup_cache(self):
        cache = MultiKeyIndex('id', ['name', 'age'])

        data = [
            {'id': 1, 'name': 'John', 'age': 20},
            {'id': 2, 'name': 'Jane', 'age': 21},
            {'id': 3, 'name': 'Jack', 'age': 22},
            {'id': 4, 'name': 'John', 'age': 23},
            {'id': 5, 'name': 'Jane', 'age': 23},
            {'id': 6, 'name': 'Jack', 'age': 22},
            {'id': 7, 'name': 'Amir', 'age': 20},
        ]

        for item in data:
            cache.add(item)

        return cache

    def test_add(self):
        cache = MultiKeyIndex('id', ['name', 'age'])
        cache.add({'id': 1, 'name': 'John', 'age': 20})

        assert cache.data['id'][1] == {'id': 1, 'name': 'John', 'age': 20}
        assert cache.data['name']['John'] == {1}
        assert cache.data['age'][20] == {1}

    def test_add_given_duplicate_id(self):
        cache = MultiKeyIndex('id', ['name', 'age'])
        cache.add({'id': 1, 'name': 'John', 'age': 20})
        cache.add({'id': 1, 'name': 'Jack', 'age': 20})

        assert cache.data['id'][1] == {'id': 1, 'name': 'Jack', 'age': 20}
        assert cache.data['name'].get('John') is None
        assert cache.data['name']['Jack'] == {1}

    def test_get(self):
        cache = self._setup_cache()
        result = cache.get_first('id', 1)
        assert result['id'] == 1
        assert result['name'] == 'John'
        assert result['age'] == 20

    def test_query(self):
        cache = self._setup_cache()
        results = cache.query({'name': 'Jack', 'age': 22})
        print(results)
