from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from app import models


def create_config():
    return models.Config.objects.create(
        sync_posts=True, sync_seconds=600, group_id=101326589, group_short_link='https://vk.com/group',
        commenting=True, comment_access_token='token123', comment_from_group=True, publish_stat=True
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
        self.assertEquals(config.negative_group_id, -101326589)

    def test_config_manager_works(self):
        """Test that config manager works"""
        config = create_config()
        db_config = models.Config.objects.get()

        self.assertEquals(config, db_config)


def create_profile():
    return models.Profile.objects.create(
        join_date=timezone.now(),
        last_sync=timezone.now(),
        first_name='Ivan',
        last_name='Fuckoff',
        sex=models.Profile.Sex.UNKNOWN
    )


class ProfileTests(TestCase):
    def setUp(self):
        self.profile = create_profile()

    def test_profile_first_and_last_name(self):
        self.assertEquals(self.profile.first_and_last_name, 'Ivan Fuckoff')

    def test_vk_link(self):
        self.assertEquals(self.profile.vk_link, 'https://vk.com/id1')

    def test_vk_link_for_post(self):
        self.assertEquals(self.profile.get_vk_link_for_post(is_development_env=True), 'Ivan Fuckoff')
        self.assertEquals(self.profile.get_vk_link_for_post(is_development_env=False), '@id1 (Ivan Fuckoff)')

    def test_profile_str(self):
        self.assertEquals(str(self.profile), 'Ivan Fuckoff')
