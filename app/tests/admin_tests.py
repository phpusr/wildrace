from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status


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
