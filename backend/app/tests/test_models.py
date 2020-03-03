from django.contrib.auth import get_user_model
from django.test import TestCase

from app import models
from app.models import Post
from app.tests import create_config, create_stat_log, create_temp_data, create_profile, create_post


class ModelTests(TestCase):
    def test_user_str(self):
        user = get_user_model().objects.create(username='phpusr')

        self.assertEquals(str(user), 'phpusr')
        self.assertEqual(user._meta.label, 'app.User')


class ConfigTests(TestCase):
    def setUp(self):
        self.config = create_config()

    def test_config_str(self):
        self.assertEquals(str(self.config), 'Config for: 88923650')

    def test_config_negative_group_id(self):
        """Test that config return negative value for group ID"""
        self.assertEquals(self.config.negative_group_id, -88923650)

    def test_config_manager_works(self):
        """Test that config manager works"""
        db_config = models.Config.objects.get()

        self.assertEquals(self.config, db_config)


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


class PostTests(TestCase):
    def test_post_str(self):
        profile = create_profile()
        post = create_post(Post.Status.SUCCESS, profile, text='3+3', number=1)
        self.assertEquals(str(post), f'Post(id: {post.id}, number: 1, text: 3+3)')

    def test_start_sum(self):
        """Test that start_sum + distance = sum_distance"""
        profile = create_profile()
        post = create_post(Post.Status.SUCCESS, profile, text='5+15=20')
        self.assertEquals(post.start_sum, 5)

        post.distance = 10
        post.sum_distance = 50
        self.assertEquals(post.start_sum, 40)


class StatLogTests(TestCase):
    def test_stat_log_str(self):
        stat_log = create_stat_log()
        self.assertEquals(str(stat_log), 'StatLog(10.01.2020 - 15.02.2020)')


class TempDataTests(TestCase):
    def test_temp_data_str(self):
        temp_data = create_temp_data()
        self.assertEquals(str(temp_data), 'TempData')
