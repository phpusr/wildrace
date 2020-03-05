from datetime import datetime, timedelta
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
        self.assertEqual(result, 'good')

    def test_get_count_days(self):
        now = datetime.now()
        self.assertIsNone(util.get_count_days(None, None))
        self.assertIsNone(util.get_count_days(None, now))
        self.assertIsNone(util.get_count_days(now, None))

        future = now + timedelta(hours=4)
        with self.assertRaises(RuntimeError):
            util.get_count_days(future, now)

        result = util.get_count_days(now, future)
        self.assertEqual(result, 1)

    def test_get_class(self):
        dt = util.get_class('datetime.datetime')
        self.assertEqual(dt, datetime)

    def test_encode_json(self):
        json = util.encode_json({'my_var': 'my_value'})
        self.assertTrue(json, '{"myVar": "my_value"')

    def test(self):
        date = datetime.utcfromtimestamp(0)
        res = util.date_to_js_unix_time(date)
        expected = int(date.timestamp() * 1000)
        self.assertEqual(res, expected)
