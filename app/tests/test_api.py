from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from app.models import Config
from app.serializers import ConfigSerializer
from app.services import vk_api_service

CONFIG_URL = reverse('config-detail', args=[1])


def create_config():
    return Config.objects.create(
        id=1,
        sync_posts=False,
        sync_seconds=300,
        group_id=88923650,
        commenting=False,
        comment_access_token='-',
        comment_from_group=False,
        publish_stat=False
    )


class PublicApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_config(self):
        """Test that authentication required to config"""
        res = self.client.get(CONFIG_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(username='phpusr', password='pass123', is_superuser=True)
        self.client.force_authenticate(self.user)
        self.config = create_config()

    def test_retrieve_config(self):
        res = self.client.get(CONFIG_URL)
        serializer = ConfigSerializer(self.config)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.data, {
            'id': 1,
            'authorize_url': vk_api_service.get_authorize_url(),
            'sync_posts': False,
            'sync_seconds': 300,
            'group_id': 88923650,
            'commenting': False,
            'comment_access_token': '-',
            'comment_from_group': False,
            'publish_stat': False
        })

    def test_update_config(self):
        payload = {'sync_seconds': 100, 'group_id': 777}
        res = self.client.patch(CONFIG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['sync_seconds'], payload['sync_seconds'])
        self.assertEqual(res.data['group_id'], payload['group_id'])
