from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from app.models import Config, StatLog
from app.serializers import ConfigSerializer, StatSerializer
from app.services import vk_api_service, stat_service
from app.tests.test_stat_service import create_runnings

STAT_URL = reverse('stat')
STAT_PUBLISH_URL = reverse('stat-publish')
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

    def test_distance_stat(self):
        """Test that stat is calculating for distance"""
        create_runnings()
        res = self.client.get(STAT_URL, {'type': 'distance'})
        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, None, None)
        serializer = StatSerializer(stat)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_date_stat(self):
        """Test that stat is calculating for dates"""
        create_runnings()
        res = self.client.get(STAT_URL, {'type': 'date'})
        stat = stat_service.calc_stat(StatLog.StatType.DATE, None, None)
        serializer = StatSerializer(stat)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_publish_stat(self):
        """Test that stat publish required authentication"""
        res = self.client.post(STAT_PUBLISH_URL, {'type': 'distance'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_config(self):
        """Test that authentication required to config"""
        res = self.client.get(CONFIG_URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(username='phpusr', password='pass123', is_staff=True)
        self.client.force_authenticate(self.user)
        self.config = create_config()

    def test_publish_stat(self):
        """Test that stat is published"""
        create_runnings()
        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, None, None)
        with patch('app.services.stat_service.publish_stat_post') as psp:
            psp.return_value = 123
            res = self.client.post(STAT_PUBLISH_URL, {'type': 'distance'})
            self.assertEqual(psp.call_count, 1)
            self.assertEqual(psp.call_args.args[0], stat)
            self.assertEqual(res.data, 123)

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
