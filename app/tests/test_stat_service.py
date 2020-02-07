from django.test import TestCase

from app.models import StatLog
from app.services import stat_service


class StatServiceTests(TestCase):

    def test_calc_stat(self):
        stat_service.calc_stat(StatLog.StatType.DISTANCE, 0, 100)
