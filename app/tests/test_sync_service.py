import os
from unittest.mock import patch

from django.test import TestCase

from app.models import Config, Post, Profile
from app.services import sync_service


def create_config():
    return Config.objects.create(
        id=1,
        sync_posts=False,
        sync_seconds=300,
        group_id=88923650,
        group_short_link='',
        commenting=False,
        comment_access_token=os.getenv('VK_ACCESS_TOKEN'),
        comment_from_group=False,
        publish_stat=False
    )


def create_comment_text(status, profile=None):
    if not profile:
        profile = Profile(id=347, first_name='Иван')
    post = Post(status=status, number=22, author=profile)
    return sync_service._create_comment_text(post, 10, 20)


class SyncServiceTests(TestCase):

    def setUp(self):
        create_config()

    def test_create_comment_text(self):
        """Test that comment text is correct"""
        self.assertEqual(
            create_comment_text(Post.Status.SUCCESS),
            '#22 пробежка: Пост успешно обработан'
        )
        self.assertEqual(
            create_comment_text(Post.Status.ERROR_SUM),
            '@id347 (Иван), #22 пробежка: Ошибка при сложении, должно быть: 20'
        )
        self.assertEqual(
            create_comment_text(Post.Status.ERROR_PARSE, Profile(id=-792, first_name='Дикий Забег')),
            '@club792 (Дикий Забег), Ошибка в формате записи, пост не распознан'
        )
        self.assertEqual(
            create_comment_text(Post.Status.ERROR_START_SUM),
            '@id347 (Иван), #22 пробежка: Ошибка в стартовой сумме, должна быть: 10'
        )
        self.assertEqual(
            create_comment_text(99),
            '@id347 (Иван), #22 пробежка: Ошибка: Не предусмотренный статус, напишите администратору'
        )

    def test_not_add_status_comment(self):
        """Test that status comment don't leave"""
        with patch('app.services.vk_api_service.add_comment_to_post') as gi:
            sync_service._add_status_comment(1, 'Status comment')
            self.assertEqual(gi.call_count, 0)

    def test_add_status_comment(self):
        """Test that status comment leave"""
        config = Config.objects.get()
        config.commenting = True
        config.save()

        with patch('app.services.vk_api_service.add_comment_to_post') as gi:
            sync_service._add_status_comment(1, 'Status comment')
            self.assertEqual(gi.call_count, 1)
