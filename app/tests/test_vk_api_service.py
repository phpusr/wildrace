import os

from django.test import TestCase

from app.models import Config
from app.services import vk_api_service


def create_config():
    return Config.objects.create(
        id=1,
        sync_posts=False,
        sync_seconds=300,
        group_id=88923650,
        group_short_link='',
        commenting=False,
        comment_access_token=os.getenv('ACCESS_TOKEN'),
        comment_from_group=False,
        publish_stat=False
    )


class VkApiTests(TestCase):

    def setUp(self):
        create_config()

    def test_login(self):
        result = vk_api_service.wall_get(0, 1)
        print(result)
        self.assertIn('count', result)
        self.assertIn('items', result)
