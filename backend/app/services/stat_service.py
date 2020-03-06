import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List

from django.conf import settings
from django.db import transaction
from django.db.models import Sum, F, Count
from django.utils import timezone

from app.models import Profile, StatLog, Post, TempData
from app.services import vk_api_service, ws_service
from app.services.ws_service import ObjectType
from app.util import find_all, get_count_days, date_to_js_unix_time, js_unix_time_to_date

logger = logging.getLogger(__name__)

MAX_NEW_RUNNERS_COUNT = 25
TOP_RUNNERS_COUNT = 5


@dataclass
class RunnerDto:
    profile: Profile
    running_count: int
    distance_sum: int


@dataclass
class StatDto:
    start_distance: Optional[int] = None
    end_distance: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    all_days_count: int = 0
    """All running days"""

    interval_days_count: int = 0
    """Interval running days count"""

    all_distance: int = 0
    """Distance for whole time in KM"""

    max_one_man_distance: RunnerDto = None
    """Max distance from one man for whole time"""

    all_training_count: int = 0
    """Training count for whole time"""

    max_one_man_training_count: RunnerDto = None
    """Max training count from one man for whole time"""

    all_runners_count: int = 0
    """Runners count for whole time"""

    interval_runners_count: int = 0
    """Runners which ran on interval"""

    new_runners: List[Profile] = None
    """New runners on interval (max: 25)"""

    new_runners_count: int = 0
    """New runners count on interval"""

    top_all_runners: List[RunnerDto] = None
    """Top of runners for whole time"""

    top_interval_runners: List[RunnerDto] = None
    """Top of runners in interval"""

    @property
    def type(self) -> StatLog.StatType:
        if self.start_distance is not None and self.end_distance is not None:
            return StatLog.StatType.DISTANCE

        return StatLog.StatType.DATE

    @property
    def distance_per_day(self) -> float:
        return self.all_distance / self.all_days_count

    @property
    def distance_per_training(self) -> float:
        return self.all_distance / self.all_training_count

    @property
    def training_count_per_day(self):
        return self.all_training_count / self.all_days_count

    def create_stat_log(self, post_id):
        if self.type == StatLog.StatType.DISTANCE:
            start_value = str(self.start_distance)
            end_value = str(self.end_distance)
        else:
            start_value = self.start_date.strftime(settings.JS_DATE_FORMAT)
            end_value = self.end_date.strftime(settings.JS_DATE_FORMAT)

        return StatLog(post_id=post_id, publish_date=timezone.now(), stat_type=self.type,
                       start_value=start_value, end_value=end_value)


@transaction.atomic
def calc_stat(stat_type: StatLog.StatType, start_range: Optional[int], end_range: Optional[int]):
    stat = StatDto()

    if stat_type == StatLog.StatType.DATE:
        if start_range is not None:
            stat.start_date = js_unix_time_to_date(start_range)
        if end_range is not None:
            # Change time at and of day
            stat.end_date = js_unix_time_to_date(end_range) + timedelta(hours=23, minutes=59, seconds=59)
    elif stat_type == StatLog.StatType.DISTANCE:
        stat.start_distance = start_range
        stat.end_distance = end_range
    else:
        raise RuntimeError(f'Unsupported stat type: {stat_type}')

    first_running = _get_one_running()
    first_int_running = _get_one_running(stat)
    last_int_running = _get_one_running(stat, direction='-')
    last_running = last_int_running

    if not first_running or not last_running or not first_int_running or not last_int_running:
        raise Post.DoesNotExist()

    if not stat.start_date:
        stat.start_date = first_int_running.date

    if not stat.end_date:
        stat.end_date = last_int_running.date

    runners = _get_runners(first_running, last_running)
    int_runners = _get_runners(first_int_running, last_int_running)

    stat.top_all_runners = runners[:TOP_RUNNERS_COUNT]
    stat.top_interval_runners = int_runners[:TOP_RUNNERS_COUNT]
    stat.all_runners_count = len(runners)
    stat.interval_runners_count = len(int_runners)
    stat.new_runners, stat.new_runners_count = _get_new_runners(int_runners, stat.start_date)

    stat.all_days_count = get_count_days(first_running.date, last_running.date)
    stat.interval_days_count = get_count_days(stat.start_date, stat.end_date)
    stat.all_distance = last_running.sum_distance
    stat.all_training_count = last_running.number

    stat.max_one_man_distance = runners[0]
    stat.max_one_man_training_count = sorted(runners, key=lambda it: it.running_count, reverse=True)[0]

    return stat


def _get_one_running(stat: StatDto = None, direction: str = '') -> Optional[Post]:
    runnings = Post.runnings.order_by(f'{direction}date')\
        .annotate(start_sum_distance=F('sum_distance')-F('distance'))

    if stat:
        if stat.start_date:
            runnings = runnings.filter(date__gte=stat.start_date)
        if stat.end_date:
            runnings = runnings.filter(date__lte=stat.end_date)
        if stat.start_distance:
            runnings = runnings.filter(start_sum_distance__gte=stat.start_distance)
        if stat.end_distance:
            runnings = runnings.filter(start_sum_distance__lt=stat.end_distance)

    return runnings.first()


def _get_runners(first_running: Post, last_running: Post) -> List[RunnerDto]:
    runners = Profile.objects\
        .filter(post__number__isnull=False, post__date__gte=first_running.date, post__date__lte=last_running.date)\
        .annotate(running_count=Count('post__number')) \
        .annotate(distance_sum=Sum('post__distance')) \
        .order_by('-distance_sum')

    return [RunnerDto(r, r.running_count, r.distance_sum) for r in runners]


def _get_new_runners(runners: List[RunnerDto], start_date: datetime):
    new_runners = find_all(runners, lambda it: it.profile.join_date >= start_date)
    new_runners = [r.profile for r in new_runners]
    new_runners = sorted(new_runners, key=lambda it: it.join_date)

    return new_runners[:MAX_NEW_RUNNERS_COUNT], len(new_runners)


def get_stat() -> dict:
    last_post = _get_one_running(direction='-')
    return {
        'distance_sum': last_post.sum_distance if last_post else 0,
        'running_count': last_post.number if last_post else 0,
        'post_count': Post.objects.count()
    }


@transaction.atomic
def update_stat():
    temp_data = TempData.objects.get()
    temp_data.last_sync_date = timezone.now()
    temp_data.save()
    ws_service.main_group_send(date_to_js_unix_time(temp_data.last_sync_date), ObjectType.LAST_SYNC_DATE)
    ws_service.main_group_send(get_stat(), ObjectType.STAT)


@transaction.atomic
def interval_publish_stat_post():
    """Publishing stat every {PUBLISHING_STAT_INTERVAL} km"""
    last_running = _get_one_running(direction='-')

    if not last_running:
        return

    last_stat_log = StatLog.objects\
        .filter(stat_type=StatLog.StatType.DISTANCE)\
        .order_by('-publish_date')\
        .first()

    start_distance = int(last_stat_log.end_value) if last_stat_log else 0
    end_distance = start_distance + settings.PUBLISHING_STAT_INTERVAL

    if last_running.sum_distance >= end_distance:
        stat = calc_stat(StatLog.StatType.DISTANCE, start_distance, end_distance)
        publish_stat_post(stat)


@transaction.atomic
def publish_stat_post(stat: StatDto) -> int:
    logger.debug(f'>> Publish stat: {stat.start_distance} -> {stat.end_distance} '
                 f'({stat.start_date} - {stat.end_date})')

    post_text = _create_post_text(stat)
    post_id = vk_api_service.create_post(post_text)['post_id']
    stat_log = stat.create_stat_log(post_id)
    stat_log.save()

    return post_id


def _create_post_text(stat: StatDto) -> str:
    is_dev = settings.DEBUG

    if stat.new_runners:
        new_runners_str = 'Поприветствуем наших новичков:\n'
        urls = [r.get_vk_link_for_post(is_dev) for r in stat.new_runners]
        new_runners_str += ', '.join(urls)
        if len(stat.new_runners) < stat.new_runners_count:
            new_runners_str += '...'
        else:
            new_runners_str += '.'
    else:
        new_runners_str = 'В этот раз без новичков'

    if stat.type == StatLog.StatType.DISTANCE:
        segment = f'{stat.start_distance}-{stat.end_distance}'
    else:
        segment = f'{stat.start_date.strftime(settings.POST_DATE_FORMAT)} - ' \
                  f'{stat.end_date.strftime(settings.POST_DATE_FORMAT)}'

    def runner_to_str(runner: RunnerDto) -> str:
        return f'- {runner.profile.get_vk_link_for_post(is_dev)} ({runner.distance_sum} км)'

    top_int_runner_urls = [runner_to_str(r) for r in stat.top_interval_runners]
    top_all_runner_urls = [runner_to_str(r) for r in stat.top_all_runners]

    s = 'СТАТИСТИКА\n\n'

    if stat.end_distance:
        s += f'Отметка в {stat.end_distance} км преодолена\n\n'
    else:
        s += f'Статистика за {segment}\n\n'

    s += f'{new_runners_str}\n\n'
    s += f'Наши итоги в цифрах:\n'
    s += '1. Количество дней бега:\n'
    s += f'- Всего - {stat.all_days_count} дн.\n'
    s += f'- Отрезок {segment} - {stat.interval_days_count} дн.\n'
    s += '2. Километраж:\n'
    s += '- Средний в день - {:.1f} км/д\n'.format(stat.distance_per_day)
    s += '- Средняя длина одной пробежки - {:.1f} км/тр\n'.format(stat.distance_per_training)
    s += '3. Тренировки:\n'
    s += f'- Всего - {stat.all_training_count} тр.\n'
    s += '- Среднее в день - {:.1f} тр.\n'.format(stat.training_count_per_day)
    s += f'- Максимум от одного человека - {stat.max_one_man_training_count.running_count} тр. ' \
         f'({stat.max_one_man_training_count.profile.get_vk_link_for_post(is_dev)})\n'
    s += '4. Бегуны:\n'
    s += f'- Всего отметилось - {stat.all_runners_count} чел.\n'
    s += f'- Отметилось на отрезке {segment} - {stat.interval_runners_count} чел.\n'
    s += f'- Новых на отрезке {segment} - {stat.new_runners_count} чел.\n'
    s += '5. Топ 5 бегунов на отрезке:\n'
    s += '\n'.join(top_int_runner_urls) + '\n'
    s += '6. Топ 5 бегунов за все время:'
    s += '\n'.join(top_all_runner_urls) + '\n\n'

    # Adding url to previous stat post
    last_log = StatLog.objects.order_by('-publish_date').first()
    if last_log:
        s += f'Предыдущий пост со статистикой: {vk_api_service.get_post_url(last_log.post_id)}\n\n'

    s += 'Всем отличного бега!\n\n'
    s += '#ДикийЗабегСтатистика'

    return s
