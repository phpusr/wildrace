from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from app import models


class ModelTests(TestCase):
    def test_user_str(self):
        user = get_user_model().objects.create(username='phpusr')

        self.assertEquals(str(user), 'phpusr')
        self.assertEqual(user._meta.label, 'app.User')


def create_config():
    return models.Config.objects.create(
        sync_posts=True, sync_seconds=600, group_id=101326589, group_short_link='https://vk.com/group',
        commenting=True, comment_access_token='token123', comment_from_group=True, publish_stat=True
    )


class ConfigTests(TestCase):
    def setUp(self):
        self.config = create_config()

    def test_config_str(self):
        self.assertEquals(str(self.config), 'Config for: https://vk.com/group')

    def test_config_negative_group_id(self):
        """Test that config return negative value for group ID"""
        self.assertEquals(self.config.negative_group_id, -101326589)

    def test_config_manager_works(self):
        """Test that config manager works"""
        db_config = models.Config.objects.get()

        self.assertEquals(self.config, db_config)


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
        self.assertEquals(self.profile.vk_link, f'https://vk.com/id{self.profile.id}')

    def test_vk_link_for_post(self):
        self.assertEquals(self.profile.get_vk_link_for_post(is_development_env=True), 'Ivan Fuckoff')
        self.assertEquals(self.profile.get_vk_link_for_post(is_development_env=False),
                          f'@id{self.profile.id} (Ivan Fuckoff)')

    def test_profile_str(self):
        self.assertEquals(str(self.profile), 'Ivan Fuckoff')


def create_post():
    profile = create_profile()
    return models.Post.objects.create(status=1, author=profile, date=timezone.now(), number=1, text='3 + 3',
                                      text_hash='1fa', distance=15, sum_distance=20, edit_reason='test',
                                      last_update=timezone.now())


class PostTests(TestCase):
    def test_post_str(self):
        post = create_post()
        self.assertEquals(str(post), f'Post(id: {post.id}, number: 1, text: 3 + 3)')

    def test_start_sum(self):
        """Test that start_sum + distance = sum_distance"""
        post = create_post()
        self.assertEquals(post.start_sum, 5)

        post.distance = 10
        post.sum_distance = 50
        self.assertEquals(post.start_sum, 40)
