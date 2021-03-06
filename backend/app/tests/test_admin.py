from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from app.models import Post
from app.tests import create_config, create_profile, create_stat_log, create_temp_data, create_post, create_admin


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = create_admin()
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
        profile = create_profile()
        post = create_post(Post.Status.SUCCESS, profile, 'Test')
        res = self.client.get(reverse('admin:app_post_change', args=[post.id]))

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, str(post))

    def test_stat_log_exists(self):
        """Test that stat log page exists"""
        stat_log = create_stat_log()
        res = self.client.get(reverse('admin:app_statlog_change', args=[stat_log.id]))

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, str(stat_log))

    def test_temp_data_exists(self):
        """Test that test data page exists"""
        temp_data = create_temp_data()
        res = self.client.get(reverse('admin:app_tempdata_change', args=[temp_data.id]))

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, str(temp_data))
