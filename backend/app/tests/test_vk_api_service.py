from unittest.mock import patch

from django.test import TestCase

from app.services import vk_api_service
from app.tests import create_config


class VkApiTests(TestCase):

    def setUp(self):
        create_config()

    def test_authorize_url(self):
        """Test authorize url"""
        authorize_url = 'https://oauth.vk.com/authorize?client_id=5344865&display=page&' \
                        'redirect_uri=https://oauth.vk.com/blank.html&scope=wall,offline&response_type=token&' \
                        'v=5.92'
        self.assertEquals(vk_api_service.get_authorize_url(), authorize_url)

    def test_get_group_url(self):
        self.assertEquals(vk_api_service.get_group_url(), 'https://vk.com/club88923650')

    def test_get_post_url(self):
        self.assertEquals(vk_api_service.get_post_url(1226), 'https://vk.com/club88923650?w=wall-88923650_1226')

    def test_get_wall_posts(self):
        """Test that wall.get return a value"""
        result = vk_api_service.get_wall_posts(0, 1)

        self.assertIn('count', result)
        self.assertIn('items', result)

    def test_get_user(self):
        """Test that users.get return a value"""
        user_id = 354515836
        result = vk_api_service.get_user(user_id)

        self.assertEquals(result['id'], user_id)
        self.assertIn('sex', result)
        self.assertIn('photo_50', result)
        self.assertIn('photo_100', result)

    def test_get_group(self):
        """Test that groups.get return a value"""
        group_id = 88923650
        result = vk_api_service.get_group(group_id)

        self.assertEquals(result['id'], group_id)
        self.assertIn('name', result)
        self.assertIn('photo_50', result)
        self.assertIn('photo_100', result)
        self.assertIn('photo_200', result)

    def test_create_post(self):
        """Test that wall.post return a value"""
        with patch('vk_api.vk_api.VkApi.method') as m:
            m.return_value = {'post_id', 1}
            result = vk_api_service.create_post('It is a new post from test')
            self.assertIn('post_id', result)

    def test_add_comment_to_post(self):
        """Test that wall.create_comment return a value"""
        with patch('vk_api.vk_api.VkApi.method') as m:
            m.return_value = {'post_id': 1}
            post_id = vk_api_service.create_post('Post for comment')['post_id']

            m.return_value = {'comment_id': 100}
            result = vk_api_service.add_comment_to_post(post_id, 'Message from test')

            self.assertEqual(m.call_count, 2)
            self.assertIn('comment_id', result)
