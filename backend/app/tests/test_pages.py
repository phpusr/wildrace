from app.models import TempData
from app.tests.test_api import create_config
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

INDEX_URL = reverse('index')


def create_temp_data():
    return TempData.objects.create(last_sync_date=timezone.now())


class PublicTests(TestCase):
    def setUp(self):
        self.client = Client()
        create_temp_data()
        create_config()

    def test_index_page(self):
        res = self.client.get(INDEX_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotContains(res, 'username')
        self.assertNotContains(res, 'isStaff')


class PrivateTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create(username='phpusr', password='123pas')
        self.client.force_login(self.user)
        create_temp_data()
        create_config()

    def test_index_page(self):
        res = self.client.get(INDEX_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, 'username')
        self.assertContains(res, 'isStaff')