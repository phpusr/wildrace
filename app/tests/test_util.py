from unittest import TestCase

from app import util


class UtilTests(TestCase):

    def test_find(self):
        people = [
            {'id': 21, 'name': 'Jack'},
            {'id': 11, 'name': 'Bob'},
            {'id': 300, 'name': 'Dude'},
            {'id': 22, 'name': 'Craig'}
        ]
        person = util.find(people, lambda it: it['id'] == 300)
        self.assertEqual(person, {'id': 300, 'name': 'Dude'})

    def test_find_all(self):
        people = [
            {'id': 21, 'name': 'Jack'},
            {'id': 11, 'name': 'Bob'},
            {'id': 300, 'name': 'Dude'},
            {'id': 22, 'name': 'Bob'}
        ]
        persons = util.find_all(people, lambda it: it['name'] == 'Bob')
        self.assertEqual(len(persons), 2)
        self.assertEqual(persons, [{'id': 11, 'name': 'Bob'}, {'id': 22, 'name': 'Bob'}])

    def test_remove_non_utf8_chars(self):
        result = util.remove_non_utf8_chars(None)
        self.assertIsNone(result)

        result = util.remove_non_utf8_chars('good')
        self.assertEquals(result, 'good')
