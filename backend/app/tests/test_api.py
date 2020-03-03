import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from app.models import StatLog, Post
from app.serializers import ConfigSerializer, StatSerializer, PostSerializer
from app.services import vk_api_service, stat_service
from app.tests import create_config, create_runnings

POSTS_URL = reverse('post-list')
STAT_URL = reverse('stat')
CONFIG_URL = reverse('config-detail', args=[1])


def post_detail_url(post_id):
    return reverse('post-detail', args=[post_id])


class PublicApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_post_list(self):
        """Test retrieving a list of posts"""
        create_runnings()
        res = self.client.get(POSTS_URL)
        posts = Post.objects.order_by('-date')[:10]
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_post_list_with_wrong_filter(self):
        """Test retrieving a list of post with wrong filter"""
        res = self.client.get(POSTS_URL, {'me': 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 0)
        self.assertEqual(len(res.data['results']), 0)

    def test_post_list_with_filter(self):
        """Test filtered retrieving a list of post"""
        create_runnings()
        res = self.client.get(POSTS_URL, {'me': 'true', 'status': Post.Status.ERROR_PARSE})
        posts = Post.objects.filter(last_update__isnull=False, status=Post.Status.ERROR_PARSE).order_by('date')
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['results'], serializer.data)

    def test_post_edit(self):
        """Test that post editing required authentication"""
        res = self.client.patch(post_detail_url(1), {'distance': 100})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_delete(self):
        """Test that post deleting required authentication"""
        res = self.client.delete(post_detail_url(1))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_stat_without_type(self):
        """Test that stat will return errors without type"""
        res = self.client.get(STAT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'type': ['This field is required.']})

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
        res = self.client.post(STAT_URL, {'type': 'distance'})
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

    def test_post_edit(self):
        """Test that post will be editing"""
        create_runnings()
        post = Post.objects.first()
        res = self.client.patch(post_detail_url(post.id), {'distance': 777})
        post.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(post.distance, 777)

    def test_post_delete(self):
        """Test that post will be deleted"""
        create_runnings()
        post = Post.objects.first()
        res = self.client.delete(post_detail_url(post.id))
        with self.assertRaises(Post.DoesNotExist):
            post.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_publish_without_type(self):
        """Test that stat will return errors without type"""
        res = self.client.post(STAT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'type': ['This field is required.']})

    def test_publish_stat(self):
        """Test that stat is published"""
        create_runnings()
        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, None, None)
        with patch('app.services.stat_service.publish_stat_post') as psp:
            psp.return_value = 123
            res = self.client.post(STAT_URL, {'type': 'distance'})
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
            'sync_seconds': 600,
            'group_id': 88923650,
            'commenting': False,
            'comment_access_token': os.getenv('VK_ACCESS_TOKEN'),
            'comment_from_group': False,
            'publish_stat': False
        })

    def test_update_config(self):
        payload = {'sync_seconds': 100, 'group_id': 777}
        res = self.client.patch(CONFIG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['sync_seconds'], payload['sync_seconds'])
        self.assertEqual(res.data['group_id'], payload['group_id'])
