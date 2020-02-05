import os

from django.test import TestCase

from app.models import Config
from app.services import sync_service


def create_config():
    return Config.objects.create(
        id=1,
        sync_posts=False,
        sync_seconds=300,
        group_id=88923650,
        group_short_link='',
        commenting=True,
        comment_access_token=os.getenv('VK_ACCESS_TOKEN'),
        comment_from_group=False,
        publish_stat=False
    )


class SyncServiceTests(TestCase):

    def setUp(self):
        create_config()

    def test_sync_posts(self):
        sync_service.sync_posts()
