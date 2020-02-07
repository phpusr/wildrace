import logging
from datetime import datetime
from typing import Optional, List

from django.conf import settings

from app.models import Profile, StatLog

logger = logging.getLogger(__name__)


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

        return StatLog(post_id=post_id, date=datetime.now(), stat_type=self.type,
                       start_value=start_value, end_value=end_value)


def calc_stat():
    pass
