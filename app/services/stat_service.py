import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, List

from django.conf import settings
from django.db.models import Sum, F
from django.utils import timezone

from app.models import Profile, StatLog, Post
from app.util import find_all, get_count_days

logger = logging.getLogger(__name__)

MAX_NEW_RUNNERS_COUNT = 25
TOP_RUNNERS_COUNT = 5


@dataclass
class RunnerDto:
    profile: Profile
    running_count: int
    distance_sum: int


class StatDto:
    start_distance: Optional[int]
    end_distance: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]

    all_days_count: int = 0
    """All running days"""

    interval_days_count: int = 0
    """Interval running days count"""

    all_distance: int = 0
    """Distance for whole time in KM"""

    max_one_man_distance: RunnerDto
    """Max distance from one man for whole time"""

    all_training_count: int = 0
    """Training count for whole time"""

    max_one_man_training_count: RunnerDto
    """Max training count from one man for whole time"""

    all_runners_count: int = 0
    """Runners count for whole time"""

    interval_runners_count: int = 0
    """Runners which ran on interval"""

    new_runners: List[Profile]
    """New runners on interval (max: 25)"""

    new_runners_count: int = 0
    """New runners count on interval"""

    top_all_runners = List[RunnerDto]
    """Top of runners for whole time"""

    top_interval_runners = List[RunnerDto]
    """Top of runners in interval"""

    @property
    def type(self):
        if self.start_distance is not None and self.end_distance is not None:
            return StatLog.StatType.DISTANCE

        return StatLog.StatType.DATE

    @property
    def distance_per_day(self) -> float:
        if self.all_days_count == 0:
            return 0

        return self.all_distance / self.all_days_count

    @property
    def distance_per_training(self) -> float:
        if self.all_training_count == 0:
            return 0

        return self.all_distance / self.all_training_count

    @property
    def training_count_per_day(self):
        if self.all_days_count == 0:
            return 0

        return self.all_training_count / self.all_days_count

    def create_stat_log(self, post_id):
        if self.type == StatLog.StatType.DISTANCE:
            start_value = str(self.start_distance)
            end_value = str(self.end_distance)
        else:
            start_value = self.start_date.strftime(settings.JS_DATE_FORMAT)
            end_value = self.end_date.strftime(settings.JS_DATE_FORMAT)

        return StatLog(post_id=post_id, date=timezone.now(), stat_type=self.type,
                       start_value=start_value, end_value=end_value)


def calc_stat(stat_type: StatLog.StatType, start_range: Optional[int], end_range: Optional[int]):
    stat = StatDto()

    if stat_type == StatLog.StatType.DATE:
        if start_range is not None:
            stat.start_date = datetime.utcfromtimestamp(start_range)

        if end_range is not None:
            # Change time at and of day
            stat.end_date = datetime.utcfromtimestamp(end_range) + timedelta(hours=23, minutes=59, seconds=59)
    elif stat_type == StatLog.StatType.DISTANCE:
        stat.start_distance = start_range
        stat.end_distance = end_range
    else:
        raise RuntimeError(f'Unsupported stat type: {stat_type}')

    first_running = _get_one_running()
    first_int_running = _get_one_running(stat)

    if not stat.start_date and first_int_running:
        stat.start_date = first_int_running.date

    last_int_running = _get_one_running(stat, direction='-')

    if not stat.end_date and last_int_running:
        stat.end_date = last_int_running.date

    last_running = last_int_running

    if not first_running or not last_running:
        raise Post.DoesNotExist()

    runners = _get_runners(first_running, last_running)
    stat.top_all_runners = runners[:TOP_RUNNERS_COUNT]
    int_runners = _get_runners(first_int_running, last_int_running)
    stat.top_interval_runners = int_runners[:TOP_RUNNERS_COUNT]

    stat.all_days_count = get_count_days(first_running.date, last_running.date)
    stat.interval_days_count = get_count_days(stat.start_date, stat.end_date)

    stat.all_distance = last_running.sum_distance if last_running else -1
    stat.max_one_man_distance = runners[0]

    stat.all_runners_count = len(runners)
    stat.interval_runners_count = len(int_runners)
    stat.new_runners, stat.new_runners_count = _get_new_runners(int_runners, stat.start_date)

    stat.all_training_count = last_running.number if last_running else -1
    stat.max_one_man_training_count = sorted(runners, lambda it: it.running_count * -1)[0]

    return stat


def _get_one_running(stat: StatDto = None, direction: str = '') -> Optional[Post]:
    runnings = Post.runnings.order_by(f'{direction}date')

    if stat.start_date:
        runnings = runnings.filter(date__gte=stat.start_date)
    if stat.end_date:
        runnings = runnings.filter(date__lte=stat.end_date)

    runnings = runnings.annotate(start_sum_distance=F('sum_distance')-F('distance'))

    if stat.start_distance:
        runnings = runnings.filter(start_sum_distance__gte=stat.start_distance)
    if stat.end_distance:
        runnings = runnings.filter(start_sum_distance__lt=stat.end_distance)

    return runnings.first()


def _get_runners(first_running: Optional[Post], last_running: Optional[Post]) -> List[RunnerDto]:
    runners = Profile.objects\
        .annotate(distance_sum=Sum('post__distance'))\
        .order_by('-distance_sum')

    if first_running:
        runners.filter(date__gte=first_running.date)
    if last_running:
        runners.filter(date__lte=last_running.date)

    return [RunnerDto(r, r.distance_sum) for r in runners]


def _get_new_runners(runners: List[RunnerDto], start_date: Optional[datetime]):
    if not start_date:
        return [], 0

    new_runners = find_all(runners, lambda it: it.join_date >= start_date)
    new_runners = sorted(new_runners, lambda it: it.join_date)

    return new_runners[:MAX_NEW_RUNNERS_COUNT], len(new_runners)
