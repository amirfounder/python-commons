from unittest import TestCase

from commons.ds.multi_key_index import MultiKeyIndex


class TestMultiKeyIndexAdd(TestCase):
    def test_add__given_duplicate_secondary_index_key__no_exception(self):
        cache = MultiKeyIndex('id', ['name'])
        cache.add({'id': 1, 'name': 'John'})
        cache.add({'id': 2, 'name': 'John'})

        assert cache.primary_index[1] == {'id': 1, 'name': 'John'}
        assert cache.primary_index[2] == {'id': 2, 'name': 'John'}
        assert cache.secondary_indices['name']['John'] == {1, 2}

    def test_add__given_duplicate_primary_index_key__overwrites(self):
        cache = MultiKeyIndex('id', ['name'])
        cache.add({'id': 1, 'name': 'John'})
        cache.add({'id': 1, 'name': 'Jack'})

        assert cache.primary_index[1] == {'id': 1, 'name': 'Jack'}

    def test_add__given_missing_primary_index_key__raises_exception(self):
        cache = MultiKeyIndex('id', ['name'])
        with self.assertRaises(KeyError):
            cache.add({'name': 'John'})

    def test_add__given_missing_secondary_index_key__raises_exception(self):
        cache = MultiKeyIndex('id', ['name'])
        with self.assertRaises(KeyError):
            cache.add({'id': 1})


class TestMultiKeyIndexQuery(TestCase):
    def _load_cache(self):
        cache = MultiKeyIndex('id', ['name', 'age', 'gender'])
        cache.add({'id': 1, 'name': 'John', 'age': 20, 'gender': 'M'})
        cache.add({'id': 2, 'name': 'John', 'age': 21, 'gender': 'M'})
        cache.add({'id': 3, 'name': 'Jack', 'age': 20, 'gender': 'M'})
        cache.add({'id': 4, 'name': 'Jack', 'age': 21, 'gender': 'M'})
        cache.add({'id': 5, 'name': 'Mary', 'age': 20, 'gender': 'F'})
        cache.add({'id': 6, 'name': 'Rose', 'age': 24, 'gender': 'F'})
        return cache

    def test_query__given_no_query__returns_all(self):
        cache = self._load_cache()
        assert len(cache.query({})) == 6

    def test_query__given_one_query__returns_all(self):
        cache = self._load_cache()
        results = cache.query({'name': 'John'})
        assert len(results) == 2
        assert results[0]['id'] == 1
        assert results[1]['id'] == 2

    def test_query__given_multiple_query__returns_all(self):
        cache = self._load_cache()
        results = cache.query({'name': 'John', 'age': 20})
        assert len(results) == 1
        assert results[0]['id'] == 1

    def test_query__given_invalid_query__returns_empty(self):
        cache = self._load_cache()
        results = cache.query({'name': 'John', 'age': 22})
        assert len(results) == 0


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

    def test_get(self):
        cache = self._setup_cache()
        result = cache.get_first('id', 1)
        assert result['id'] == 1
        assert result['name'] == 'John'
        assert result['age'] == 20
