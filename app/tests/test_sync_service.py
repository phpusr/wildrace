import os
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from app.enums import EventType
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
        comment_access_token='-',
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
        self.config = create_config()
        self.profile = Profile.objects.create(join_date=timezone.now(), first_name='Иван', sex=Profile.Sex.MALE)

    def test_find_profile(self):
        """Test that profile exists in DB"""
        vk_post = {'from_id': self.profile.id}
        db_profiles = list(Profile.objects.all())
        result = sync_service._find_or_create_profile(vk_post, timezone.now(), db_profiles)
        self.assertEqual(result, self.profile)

    def test_create_profile(self):
        """Test that profile will receive from vk and will save to DB"""
        vk_post = {'from_id': 100}
        db_profiles = []
        post_date = timezone.now()
        with patch('app.services.vk_api_service.get_user') as gi:
            gi.return_value = {'id': 100, 'first_name': 'Ivan', 'last_name': 'Drago', 'sex': 2, 'photo_50': '50.jpg',
                               'photo_100': '100.jpg'}

            result = sync_service._find_or_create_profile(vk_post, post_date, db_profiles)
            self.assertEqual(gi.call_count, 1)
            self.assertEqual(gi.call_args.args[0], 100)
            self.assertEqual(result.id, 100)
            self.assertEqual(result.join_date, post_date)
            self.assertEqual(result.first_name, 'Ivan')
            self.assertEqual(result.last_name, 'Drago')
            self.assertEqual(result.photo_50, '50.jpg')
            self.assertEqual(result.photo_100, '100.jpg')

    def test_create_group(self):
        """Test that group will receive and save to DB"""
        vk_post = {'from_id': -100}
        db_profiles = []
        post_date = timezone.now()
        with patch('app.services.vk_api_service.get_group') as gi:
            gi.return_value = {'name': 'Wild Race', 'photo_50': '50.jpg', 'photo_100': '100.jpg',
                               'photo_200': '200.jpg'}

            result = sync_service._find_or_create_profile(vk_post, post_date, db_profiles)
            self.assertEqual(gi.call_count, 1)
            self.assertEqual(gi.call_args.args[0], 100)
            self.assertEqual(result.id, -100)
            self.assertEqual(result.join_date, post_date)
            self.assertEqual(result.first_name, 'Wild Race')
            self.assertEqual(result.photo_50, '50.jpg')
            self.assertEqual(result.photo_100, '100.jpg')
            self.assertEqual(result.photo_200, '200.jpg')

    def analyze_post_text(self, text, new_post_number, new_sum_distance, status):
        text_hash = 'hash'
        last_sum_distance = 100
        last_post_number = 22
        post = Post(author=self.profile, date=timezone.now())
        with patch('app.services.sync_service._create_comment_text') as gi:
            sync_service._analyze_post_text(text, 'hash', last_sum_distance, last_post_number, post,
                                            EventType.CREATE)
            self.assertEqual(post.text, text)
            self.assertEqual(post.text_hash, text_hash)
            self.assertEqual(post.status, status)
            self.assertEqual(post.number, new_post_number)
            self.assertEqual(post.sum_distance, new_sum_distance)

            self.assertEqual(gi.call_count, 1)
            self.assertEqual(gi.call_args.args[0], post)
            self.assertEqual(gi.call_args.args[1], last_sum_distance)
            self.assertEqual(gi.call_args.args[2], new_sum_distance)

    def test_analyze_post_text(self):
        """Test that analyze post text is correct"""
        self.analyze_post_text(
            text='100 + 5 = 105',
            new_post_number=23,
            new_sum_distance=105,
            status=Post.Status.SUCCESS
        )
        self.analyze_post_text(
            text='100 + 5 = 104',
            new_post_number=23,
            new_sum_distance=105,
            status=Post.Status.ERROR_SUM
        )
        self.analyze_post_text(
            text='101 + 5 = 105',
            new_post_number=23,
            new_sum_distance=105,
            status=Post.Status.ERROR_START_SUM
        )
        self.analyze_post_text(
            text='text',
            new_post_number=None,
            new_sum_distance=None,
            status=Post.Status.ERROR_PARSE
        )

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

    def create_post(self, status, number, text, distance, sum_distance):
        return Post.objects.create(
            author=self.profile,
            status=status,
            date=timezone.now(),
            text=text,
            text_hash='hash',
            number=number,
            distance=distance,
            sum_distance=sum_distance
        )

    def test_update_next_posts(self):
        """Test that next posts will be updated"""
        self.create_post(Post.Status.SUCCESS, 1, '0+10=10', 10, 10)
        updated_post = self.create_post(Post.Status.ERROR_PARSE, None, 'text', None, None)
        changed_post = self.create_post(Post.Status.SUCCESS, 3, '15+6=21', 6, 21)

        with patch('app.services.sync_service._create_comment_text') as gi:
            sync_service.update_next_posts(updated_post)
            self.assertEqual(gi.call_count, 1)

        changed_post_new = Post.objects.get(id=changed_post.id)
        self.assertEqual(changed_post_new.status, Post.Status.ERROR_START_SUM)
        self.assertEqual(changed_post_new.number, 2)
        self.assertEqual(changed_post_new.sum_distance, 16)

    def test_update_next_posts_2(self):
        """Test that next posts will be updated"""
        self.create_post(Post.Status.SUCCESS, 1, '0+10=10', 10, 10)
        updated_post = self.create_post(Post.Status.SUCCESS, 2, '10+5=15', 5, 15)
        changed_post1 = self.create_post(Post.Status.SUCCESS, 3, '15+6=21', 6, 21)
        self.create_post(Post.Status.ERROR_PARSE, None, 'text', None, None)
        changed_post2 = self.create_post(Post.Status.SUCCESS, 4, '21+3=24', 3, 24)
        self.create_post(Post.Status.SUCCESS, 5, '59+11=70', 11, 70)

        updated_post.sum_distance = 50
        with patch('app.services.sync_service._create_comment_text') as gi:
            sync_service.update_next_posts(updated_post)
            self.assertEqual(gi.call_count, 2)

        changed_post1_new = Post.objects.get(id=changed_post1.id)
        self.assertEqual(changed_post1_new.status, Post.Status.ERROR_START_SUM)
        self.assertEqual(changed_post1_new.sum_distance, 56)

        changed_post2_new = Post.objects.get(id=changed_post2.id)
        self.assertEqual(changed_post2_new.status, Post.Status.ERROR_START_SUM)
        self.assertEqual(changed_post2_new.sum_distance, 59)

