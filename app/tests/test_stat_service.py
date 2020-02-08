from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from app.models import StatLog, Profile, Post
from app.services import stat_service
from app.services.stat_service import RunnerDto

DATA = """
 2015-09-01 03:56:09 |  39752943 | Сергей     | Щеднов       |        4
 2015-09-01 22:15:01 |   8429458 | Иван       | Решетов      |       12
 2015-09-02 02:56:41 |  82121484 | Евгений    | Саксонов     |        5
 2015-09-02 03:02:30 |  84566235 | Александр  | Фомин        |        2
 2015-09-02 05:10:44 |  18273238 | Данил      | Нечаев       |        3
 2015-09-03 02:13:31 |   2437792 | Станислав  | Карлштремс   |        4
 2015-09-03 03:19:02 |  11351451 | Александр  | Зиангиров    |        5
 2015-09-03 04:26:04 |  39752943 | Сергей     | Щеднов       |        5
 2015-09-03 04:38:02 |  63399502 | Сергей     | Губин        |        8
 2015-09-03 10:53:35 | 117963335 | Анастасия  | Литвинцева   |       16
 2015-09-03 15:26:13 | 258765420 | Денис      | Карелин      |        5
 2015-09-03 17:01:38 | 282180599 | Юлия       | Гайнетдинова |        2
 2015-09-03 17:16:16 |  10811344 | Данис      | Султангужин  |        6
 2015-09-04 01:39:39 |   2437792 | Станислав  | Карлштремс   |        5
 2015-09-04 02:55:57 |  84566235 | Александр  | Фомин        |        3
 2015-09-04 03:03:23 |   1553750 | Дмитрий    | Пыргаев      |        5
 2015-09-04 03:22:14 |  63399502 | Сергей     | Губин        |       12
 2015-09-04 03:46:21 | 282180599 | Юлия       | Гайнетдинова |        2
 2015-09-04 06:43:31 |  52649788 | Ирина      | Жукова       |        4
 2015-09-04 07:12:15 | 151575104 | Роман      | Горобинский  |        4
"""


def create_or_get_profile(profile_id, first_name, last_name, date):
    profile = Profile.objects.filter(pk=profile_id).first()
    if profile:
        return profile

    return Profile.objects.create(pk=profile_id, first_name=first_name, last_name=last_name,
                                  join_date=date, sex=Profile.Sex.MALE)


def create_running(number, profile, distance, sum_distance, date):
    return Post.objects.create(status=Post.Status.SUCCESS, number=number, author=profile, distance=distance,
                               sum_distance=sum_distance, date=date)


def create_runnings():
    number = 0
    sum_distance = 0
    runnings = []
    for row in DATA.split('\n'):
        if not row:
            continue

        number += 1
        props = row.split('|')
        date = datetime.strptime(props[0].strip(), '%Y-%m-%d %H:%M:%S') \
            .astimezone(timezone.get_default_timezone())
        profile_id = int(props[1].strip())
        first_name = props[2].strip()
        last_name = props[3].strip()
        distance = int(props[4].strip())
        sum_distance += distance

        profile = create_or_get_profile(profile_id, first_name, last_name, date)
        running = create_running(number, profile, distance, sum_distance, date)
        runnings.append(running)
    return runnings


def create_date(year, month, day, hour, minute, second):
    return datetime(year, month, day, hour, minute, second).astimezone(timezone.get_current_timezone())


class StatServiceTests(TestCase):

    def setUp(self):
        create_runnings()

    def test_calc_stat_without_params(self):
        """Test that test_calc_stat raises RuntimeError without params"""
        with self.assertRaises(RuntimeError):
            stat_service.calc_stat(None, None, None)

    def test_calc_stat_all_time(self):
        """Test that stat is right for whole time"""
        stat = stat_service.calc_stat(StatLog.StatType.DATE, None, None)

        max_one_man_distance = RunnerDto(Profile.objects.get(pk=63399502), 2, 20)
        max_one_man_training_count = max_one_man_distance
        top_all_runners = [
            RunnerDto(Profile.objects.get(pk=63399502), 2, 20),
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=8429458), 1, 12),
            RunnerDto(Profile.objects.get(pk=2437792), 2, 9),
            RunnerDto(Profile.objects.get(pk=39752943), 2, 9)
        ]
        top_int_runners = top_all_runners

        self.assertIsNotNone(stat)
        self.assertIsNone(stat.start_distance)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, create_date(2015, 9, 1, 3, 56, 9))
        self.assertEqual(stat.end_date, create_date(2015, 9, 4, 7, 12, 15))
        self.assertEqual(stat.all_days_count, 4)
        self.assertEqual(stat.interval_days_count, 4)
        self.assertEqual(stat.max_one_man_distance, max_one_man_distance)
        self.assertEqual(stat.all_training_count, 20)
        self.assertEqual(stat.max_one_man_training_count, max_one_man_training_count)
        self.assertEqual(stat.all_runners_count, 15)
        self.assertEqual(stat.new_runners, list(Profile.objects.order_by('join_date')))
        self.assertEqual(stat.new_runners_count, 15)
        self.assertEqual(stat.top_all_runners, top_all_runners)
        self.assertEqual(stat.top_interval_runners, top_int_runners)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertAlmostEqual(stat.distance_per_day, 28, 2)
        self.assertAlmostEqual(stat.distance_per_training, 5.6, 2)
        self.assertAlmostEqual(stat.training_count_per_day, 5, 2)
