from datetime import datetime, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from app.models import StatLog, Profile, Post, TempData
from app.services import stat_service
from app.services.stat_service import RunnerDto, StatDto

DATA = """
 2015-09-01 03:56:09 |  39752943 | Сергей     | Щеднов       |        4
 2015-09-01 18:23:34 |	-1013265 | Дикий"	  | Забег        |		
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
    if not distance:
        status = Post.Status.ERROR_PARSE
        number = None
        sum_distance = None
    else:
        status = Post.Status.SUCCESS

    return Post.objects.create(status=status, number=number, author=profile, distance=distance,
                               sum_distance=sum_distance, date=date)


def create_runnings():
    number = 0
    sum_distance = 0
    runnings = []
    for row in DATA.split('\n'):
        if not row:
            continue

        props = row.split('|')
        date = datetime.strptime(props[0].strip(), '%Y-%m-%d %H:%M:%S') \
            .astimezone(timezone.get_default_timezone())
        profile_id = int(props[1].strip())
        first_name = props[2].strip()
        last_name = props[3].strip()
        try:
            distance = int(props[4].strip())
            sum_distance += distance
            number += 1
        except ValueError:
            distance = None

        profile = create_or_get_profile(profile_id, first_name, last_name, date)
        running = create_running(number, profile, distance, sum_distance, date)
        runnings.append(running)
    return runnings


def create_date(year, month, day, hour=0, minute=0, second=0):
    return datetime(year, month, day, hour, minute, second).astimezone(timezone.get_current_timezone())


class StatServiceTests(TestCase):

    def test_calc_stat_without_data(self):
        """Test that raised exception if no data in DB"""
        with self.assertRaises(Post.DoesNotExist):
            stat_service.calc_stat(StatLog.StatType.DISTANCE, None, None)

    def test_calc_stat_without_params(self):
        """Test that test_calc_stat raises RuntimeError without params"""
        create_runnings()
        with self.assertRaises(RuntimeError):
            stat_service.calc_stat(None, None, None)

        """Test without start distance"""
        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, None, 100)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertIsNone(stat.start_distance)
        self.assertEqual(stat.end_distance, 100)
        self.assertEqual(stat.start_date, create_date(2015, 9, 1, 3, 56, 9))
        self.assertEqual(stat.end_date, create_date(2015, 9, 4, 3, 22, 14))

        """Test without end distance"""
        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, 16, None)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertEqual(stat.start_distance, 16)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, create_date(2015, 9, 2, 2, 56, 41))
        self.assertEqual(stat.end_date, create_date(2015, 9, 4, 7, 12, 15))

        """Test without start date"""
        start_date = None
        end_date = create_date(2015, 9, 3)
        stat = stat_service.calc_stat(StatLog.StatType.DATE, start_date, int(end_date.timestamp()))
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertIsNone(stat.start_distance)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, create_date(2015, 9, 1, 3, 56, 9))
        self.assertEqual(stat.end_date, create_date(2015, 9, 3, 23, 59, 59))

        """Test without end date"""
        start_date = create_date(2015, 9, 3, 4, 38, 2)
        end_date = None
        stat = stat_service.calc_stat(StatLog.StatType.DATE, int(start_date.timestamp()), end_date)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertIsNone(stat.start_distance)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, start_date)
        self.assertEqual(stat.end_date, create_date(2015, 9, 4, 7, 12, 15))

    def test_calc_stat_all_time(self):
        """Test that stat is right for whole time"""
        create_runnings()
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
        new_runners = list(Profile.objects.exclude(pk=-1013265).order_by('join_date'))

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
        self.assertEqual(stat.new_runners, new_runners)
        self.assertEqual(stat.new_runners_count, 15)
        self.assertEqual(stat.top_all_runners, top_all_runners)
        self.assertEqual(stat.top_interval_runners, top_int_runners)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertAlmostEqual(stat.distance_per_day, 28, 2)
        self.assertAlmostEqual(stat.distance_per_training, 5.6, 2)
        self.assertAlmostEqual(stat.training_count_per_day, 5, 2)

    def test_calc_stat_for_dates(self):
        """Test that stat is right between 2 dates"""
        create_runnings()

        start_date = create_date(2015, 9, 2)
        end_date = create_date(2015, 9, 3)

        stat = stat_service.calc_stat(
            StatLog.StatType.DATE,
            start_range=int(start_date.timestamp()),
            end_range=int(end_date.timestamp())
        )

        max_one_man_distance = RunnerDto(Profile.objects.get(pk=117963335), 1, 16)
        max_one_man_training_count = RunnerDto(Profile.objects.get(pk=39752943), 2, 9)

        top_all_runners = [
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=8429458), 1, 12),
            RunnerDto(Profile.objects.get(pk=39752943), 2, 9),
            RunnerDto(Profile.objects.get(pk=63399502), 1, 8),
            RunnerDto(Profile.objects.get(pk=10811344), 1, 6)
        ]

        top_interval_runners = [
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=63399502), 1, 8),
            RunnerDto(Profile.objects.get(pk=10811344), 1, 6),
            RunnerDto(Profile.objects.get(pk=11351451), 1, 5),
            RunnerDto(Profile.objects.get(pk=39752943), 1, 5)
        ]

        self.assertIsNone(stat.start_distance)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, start_date)
        self.assertEqual(stat.end_date, create_date(2015, 9, 3, 23, 59, 59))
        self.assertEqual(stat.all_days_count, 3)
        self.assertEqual(stat.interval_days_count, 2)
        self.assertEqual(stat.all_distance, 77)
        self.assertEqual(stat.max_one_man_distance, max_one_man_distance)
        self.assertEqual(stat.all_training_count, 13)
        self.assertEqual(stat.max_one_man_training_count, max_one_man_training_count)
        self.assertEqual(stat.all_runners_count, 12)
        self.assertEqual(stat.interval_runners_count, 11)
        self.assertEqual(len(stat.new_runners), 10)
        self.assertEqual(stat.new_runners_count, 10)
        self.assertEqual(stat.top_all_runners, top_all_runners)
        self.assertEqual(stat.top_interval_runners, top_interval_runners)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertAlmostEqual(stat.distance_per_day, 25.67, 2)
        self.assertAlmostEqual(stat.distance_per_training, 5.92, 2)
        self.assertAlmostEqual(stat.training_count_per_day, 4.33, 2)

    def test_calc_stat_for_distances(self):
        """Test that stat is right between 2 distances"""
        create_runnings()

        start_distance = 16
        end_distance = 77

        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, start_distance, end_distance)
        self.assertIsNotNone(stat)

        max_one_man_distance = RunnerDto(Profile.objects.get(pk=117963335), 1, 16)
        max_one_man_training_count = RunnerDto(Profile.objects.get(pk=39752943), 2, 9)

        top_all_runners = [
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=8429458), 1, 12),
            RunnerDto(Profile.objects.get(pk=39752943), 2, 9),
            RunnerDto(Profile.objects.get(pk=63399502), 1, 8),
            RunnerDto(Profile.objects.get(pk=10811344), 1, 6)
        ]

        top_interval_runners = [
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=63399502), 1, 8),
            RunnerDto(Profile.objects.get(pk=10811344), 1, 6),
            RunnerDto(Profile.objects.get(pk=11351451), 1, 5),
            RunnerDto(Profile.objects.get(pk=39752943), 1, 5)
        ]

        self.assertEqual(stat.start_distance, start_distance)
        self.assertEqual(stat.end_distance, end_distance)
        self.assertEqual(stat.start_date, create_date(2015, 9, 2, 2, 56, 41))
        self.assertEqual(stat.end_date, create_date(2015, 9, 3, 17, 16, 16))
        self.assertEqual(stat.all_days_count, 3)
        self.assertEqual(stat.interval_days_count, 2)
        self.assertEqual(stat.all_distance, 77)
        self.assertEqual(stat.max_one_man_distance, max_one_man_distance)
        self.assertEqual(stat.all_training_count, 13)
        self.assertEqual(stat.max_one_man_training_count, max_one_man_training_count)
        self.assertEqual(stat.all_runners_count, 12)
        self.assertEqual(stat.interval_runners_count, 11)
        self.assertEqual(len(stat.new_runners), 10)
        self.assertEqual(stat.new_runners_count, 10)
        self.assertEqual(stat.top_all_runners, top_all_runners)
        self.assertEqual(stat.top_interval_runners, top_interval_runners)
        self.assertEqual(stat.type, StatLog.StatType.DISTANCE)
        self.assertAlmostEqual(stat.distance_per_day, 25.67, 2)
        self.assertAlmostEqual(stat.distance_per_training, 5.92, 2)
        self.assertAlmostEqual(stat.training_count_per_day, 4.33, 2)

    def test_create_stat_log(self):
        """Test that create_stat_log return correct values"""
        create_runnings()
        stat = stat_service.calc_stat(StatLog.StatType.DATE, None, None)

        stat_log = stat.create_stat_log(100)
        self.assertIsNone(stat_log.id)
        self.assertEqual(stat_log.post_id, 100)
        self.assertEqual(stat_log.stat_type, StatLog.StatType.DATE)
        self.assertEqual(stat_log.start_value, '2015-09-01')
        self.assertEqual(stat_log.end_value, '2015-09-04')

        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, 100, 200)
        stat_log = stat.create_stat_log(200)
        self.assertIsNone(stat_log.id)
        self.assertEqual(stat_log.post_id, 200)
        self.assertEqual(stat_log.stat_type, StatLog.StatType.DISTANCE)
        self.assertEqual(stat_log.start_value, '100')
        self.assertEqual(stat_log.end_value, '200')

    def test_get_stat(self):
        """Test that get_stat return correct values"""
        stat = stat_service.get_stat()
        self.assertEqual(stat, {
            'distance_sum': 0,
            'running_count': 0,
            'post_count': 0
        })

        create_runnings()
        stat = stat_service.get_stat()
        self.assertEqual(stat, {
            'distance_sum': 112,
            'running_count': 20,
            'post_count': 21
        })

    def test_update_stat(self):
        """Test that update stat correct update last_sync_date"""
        temp_data = TempData.objects.create(
            last_sync_date=timezone.now() - timedelta(days=100)
        )

        before_date = timezone.now()
        stat_service.update_stat()
        after_date = timezone.now()
        temp_data.refresh_from_db()

        self.assertGreaterEqual(temp_data.last_sync_date, before_date)
        self.assertLessEqual(temp_data.last_sync_date, after_date)

    @patch('app.services.vk_api_service.create_post', return_value={'post_id': 123})
    @patch('app.services.stat_service._create_post_text', return_value='Post text')
    def test_interval_publish_stat_post(self, create_text, create_post):
        """Test that stat is publishing through interval"""
        with self.settings(PUBLISHING_STAT_INTERVAL=50):
            stat_service.interval_publish_stat_post()
            self.assertEqual(create_text.call_count, 0)
            self.assertEqual(create_post.call_count, 0)

            create_runnings()
            stat_service.interval_publish_stat_post()
            last_stat_log = StatLog.objects.last()
            self.assertEqual(create_text.call_count, 1)
            self.assertEqual(create_post.call_count, 1)
            self.assertEqual(create_post.call_args.args, ('Post text',))
            self.assertEqual(last_stat_log.stat_type, StatLog.StatType.DISTANCE)
            self.assertEqual(last_stat_log.start_value, '0')
            self.assertEqual(last_stat_log.end_value, '50')

            stat_service.interval_publish_stat_post()
            last_stat_log = StatLog.objects.last()
            self.assertEqual(create_text.call_count, 2)
            self.assertEqual(create_post.call_count, 2)
            self.assertEqual(create_post.call_args.args, ('Post text',))
            self.assertEqual(last_stat_log.stat_type, StatLog.StatType.DISTANCE)
            self.assertEqual(last_stat_log.start_value, '50')
            self.assertEqual(last_stat_log.end_value, '100')

            stat_service.interval_publish_stat_post()
            self.assertEqual(create_text.call_count, 2)
            self.assertEqual(create_post.call_count, 2)

    @patch('app.services.vk_api_service.create_post', return_value={'post_id': 123})
    @patch('app.services.stat_service._create_post_text', return_value='Post text')
    def test_publish_stat_post(self, create_text, create_post):
        """Test that stat is publishing"""
        stat = StatDto(start_distance=1000, end_distance=2000)
        post_id = stat_service.publish_stat_post(stat)
        self.assertEqual(post_id, 123)
        self.assertEqual(create_text.call_count, 1)
        self.assertEqual(create_post.call_count, 1)
        self.assertEqual(create_post.call_args.args, ('Post text',))

        stat_log = StatLog.objects.last()
        self.assertEqual(StatLog.objects.count(), 1)
        self.assertEqual(stat_log.start_value, '1000')
        self.assertEqual(stat_log.end_value, '2000')
