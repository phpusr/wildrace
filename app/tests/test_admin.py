from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from app.tests.test_models import create_config, create_profile, create_post, create_stat_log


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create(username='phpusr', password='123', is_staff=True,
                                                          is_superuser=True)
        self.client.force_login(self.admin_user)

    def test_users_listed(self):
        """Test that users are listed on user page"""
        res = self.client.get(reverse('admin:app_user_changelist'))
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, self.admin_user.username)

        res = self.client.get(reverse('admin:app_user_change', args=[self.admin_user.id]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, self.admin_user.username)

    def test_config_exists(self):
        """Test that config page exists"""
        config = create_config()
        res = self.client.get(reverse('admin:app_config_change', args=[config.id]))

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, str(config))

    def test_profile_exists(self):
        """Test that profile page exists"""
        profile = create_profile()
        res = self.client.get(reverse('admin:app_profile_change', args=[profile.id]))

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, str(profile))

    def test_post_exists(self):
        """Test that post page exists"""
        post = create_post()
        res = self.client.get(reverse('admin:app_post_change', args=[post.id]))

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, str(post))

    def test_stat_log_exists(self):
        """Test that stat log page exists"""
        stat_log = create_stat_log()
        res = self.client.get(reverse('admin:app_statlog_change', args=[stat_log.id]))

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, str(stat_log))