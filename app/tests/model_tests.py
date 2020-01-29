from django.contrib.auth import get_user_model
from django.test import TestCase

from app import models


def create_config():
    return models.Config.objects.create(
        sync_posts=True, sync_seconds=600, group_id=101326589, group_short_link='https://vk.com/group', commenting=True,
        comment_access_token='token123', comment_from_group=True, publish_stat=True
    )


class ModelTests(TestCase):
    def test_user_str(self):
        user = get_user_model().objects.create(username='phpusr')

        self.assertEquals(str(user), 'phpusr')
        self.assertEqual(user._meta.label, 'app.User')

    def test_config_str(self):
        self.assertEquals(str(create_config()), 'Config for: https://vk.com/group')

    def test_config_negative_group_id(self):
        """Test that config return negative value for group ID"""
        config = create_config()
        self.assertEquals(config.negative_group_id, -500)

    def test_config_manager_works(self):
        """Test that config manager works"""
        config = create_config()
        db_config = models.Config.objects.get()

        self.assertEquals(config, db_config)
