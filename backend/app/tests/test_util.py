from datetime import datetime, timedelta

from django.test import TestCase

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

    def test_date_to_js_unix_time(self):
        date = datetime.utcfromtimestamp(0)
        res = util.date_to_js_unix_time(date)
        expected = int(date.timestamp() * 1000)
        self.assertEqual(res, expected)

    def test_simple_url(self):
        url = 'redis://localhost:6379'
        res = util.split_url(url)
        expected = {
            'protocol': 'redis',
            'username': '',
            'password': '',
            'host': 'localhost',
            'port': 6379
        }
        self.assertEqual(res, expected)

    def test_split_amazon_redis_url(self):
        url = 'redis://h:p548d87ab98d6c5688858f7e06271986ad20b2c35216705f74598ef04b53b4933' \
              '@ec2-52-212-215-87.eu-west-1.compute.amazonaws.com:13519'
        res = util.split_url(url)
        expected = {
            'protocol': 'redis',
            'username': 'h',
            'password': 'p548d87ab98d6c5688858f7e06271986ad20b2c35216705f74598ef04b53b4933',
            'host': 'ec2-52-212-215-87.eu-west-1.compute.amazonaws.com',
            'port': 13519
        }
        self.assertEqual(res, expected)

    def test_not_support_url(self):
        url = 'redis://localhost'
        with self.assertRaises(ValueError):
            util.split_url(url)
