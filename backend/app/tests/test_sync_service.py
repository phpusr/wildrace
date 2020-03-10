from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from app.models import Config, Post, Profile
from app.services import sync_service
from app.tests import create_config, create_comment_text, create_post, create_vk_post
from ws.ws_service import EventType


class SyncServiceTests(TestCase):

    def setUp(self):
        self.config = create_config()
        self.profile = Profile.objects.create(join_date=timezone.now(), first_name='Ivan', sex=Profile.Sex.MALE)

    def create_vk_post(self, post_id, text, timestamp=None):
        return create_vk_post(post_id, self.profile.id, text, timestamp)

    def create_post(self, status, text, number=None, post_id=None, date=None,
                    timestamp=None):
        return create_post(status, self.profile, text, number, post_id, date, timestamp)

    def test_transactional_sync_posts(self):
        """Test that sync post runs in transaction"""
        items = [
            self.create_vk_post(5, '18+4=22'),
            self.create_vk_post('a', '18+4=22'),
        ]
        with patch('app.services.vk_api_service.get_wall_posts') as gwp:
            gwp.return_value = {'count': len(items), 'items': items}
            try:
                sync_service.sync_posts()
            except ValueError:
                pass
            self.assertEqual(Post.objects.count(), 0)

    def test_sync_posts_many_blocks(self):
        sync_service.DOWNLOAD_POST_COUNT = 1
        items = [
            self.create_vk_post(2, '18+4=22'),
            self.create_vk_post(1, '18+4=22'),
        ]
        with patch('app.services.vk_api_service.get_wall_posts') as get_wall_posts:
            get_wall_posts.side_effect = [
                {'count': len(items), 'items': items[1:2]},
                {'count': len(items), 'items': items[1:2]},
                {'count': len(items), 'items': items},
                {'count': len(items), 'items': items}
            ]
            sync_service.sync_posts()
            self.assertEqual(get_wall_posts.call_count, 2*2)

    def test_sync_posts(self):
        """Test that sync_posts call get_wall_posts 2 times"""
        with patch('app.services.vk_api_service.get_wall_posts') as gi:
            gi.return_value = {'count': 0, 'items': []}
            sync_service.sync_posts()
            self.assertEqual(gi.call_count, 2)

    def test_sync_posts_error_post_number(self):
        """Test that number of post in DB > number of post in VK"""
        self.create_post(Post.Status.ERROR_PARSE, 'text',
                         date=timezone.now() - timedelta(days=5, milliseconds=1))
        with self.assertRaises(RuntimeError):
            with patch('app.services.vk_api_service.get_wall_posts') as gi:
                gi.return_value = {'count': 0, 'items': []}
                sync_service.sync_posts()

    @patch('app.services.vk_api_service.get_wall_posts')
    @patch('app.services.stat_service.update_stat')
    @patch('time.sleep')
    def test_sync_posts_need_sync(self, ts, us, gwp):
        """Test that _sync_block_posts calls 2 times"""
        gwp.return_value = {'count': 1}
        ts.return_value = True
        with patch('app.services.sync_service._sync_block_posts') as sbp:
            sbp.side_effect = [0, 1]
            sync_service.sync_posts()
            self.assertEqual(gwp.call_count, 2)
            self.assertEqual(ts.call_count, 1)
            self.assertEqual(us.call_count, 1)
            self.assertEqual(sbp.call_count, 2)

    def test_sync_block_posts_count_changed(self):
        """Test sync block if vk posts count changed"""
        with patch('app.services.vk_api_service.get_wall_posts') as gi:
            gi.return_value = {'count': 0}
            result = sync_service._sync_block_posts(vk_post_count=130, download_count=100)
            self.assertEqual(gi.call_count, 1)
            self.assertEqual(gi.call_args.args[0], 30)
            self.assertEqual(gi.call_args.args[1], 100)
            self.assertEqual(result, 0)

    def test_sync_block_posts(self):
        """Test sync block"""
        items = [
            self.create_vk_post(1, '0+10=10', 1),
            self.create_vk_post(2, '10+5=15', 2),
            self.create_vk_post(4, '15+3=18', 3),
            self.create_vk_post(5, '18+4=22', 4)
        ]
        items.reverse()

        self.create_post(Post.Status.SUCCESS, items[-1]['text'], 1, post_id=items[-1]['id'],
                         timestamp=items[-1]['date'])
        self.create_post(Post.Status.ERROR_SUM, '10+5=16', 2, post_id=items[-2]['id'], timestamp=items[-2]['date'])
        self.create_post(Post.Status.ERROR_SUM, 'some', post_id=3)

        with patch('app.services.vk_api_service.get_wall_posts') as gi:
            gi.return_value = {
                'count': len(items),
                'items': items
            }
            result = sync_service._sync_block_posts(len(items), 100)
            self.assertEqual(result, len(items))

    @patch('app.services.sync_service._analyze_post_text')
    def test_sync_block_posts_with_last_update(self, apt):
        items = [self.create_vk_post(1, 'text')]
        post = self.create_post(Post.Status.SUCCESS, '0+5=5', 1)
        post.last_update = timezone.now()
        post.save()

        with patch('app.services.vk_api_service.get_wall_posts') as gi:
            gi.return_value = {
                'count': len(items),
                'items': items
            }
            result = sync_service._sync_block_posts(1, 100)
            self.assertEqual(result, 1)
            self.assertEqual(apt.call_count, 0)

    def test_remove_deleted_posts(self):
        result = sync_service._remove_deleted_posts([], [])
        self.assertEqual(result, [])

        vk_posts = [{'id': 123}]

        post1 = self.create_post(Post.Status.SUCCESS, 'text', post_id=123)
        post2 = self.create_post(Post.Status.SUCCESS, 'text', post_id=124)
        post3 = self.create_post(Post.Status.SUCCESS, 'text', post_id=125,
                                 date=timezone.now() - timedelta(days=5, milliseconds=1))

        posts = [post1, post2, post3]
        result = sync_service._remove_deleted_posts(vk_posts, posts)

        self.assertEqual(len(result), 1)
        self.assertEqual(result, [124])
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts, [post1, post3])

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

    def test_update_next_posts_transactional(self):
        """Test that update_next_post runs in transaction"""
        updated_post = self.create_post(Post.Status.SUCCESS, '0+5=5', 1)
        next_post1 = self.create_post(Post.Status.SUCCESS, '5+15=20', 2)

        updated_post.sum_distance = 10

        def raise_error(post, *args):
            if post == next_post1:
                raise RuntimeError('Ooops!')

        with patch('app.services.sync_service._create_comment_text') as apt:
            apt.side_effect = raise_error
            try:
                sync_service.update_next_posts(updated_post)
            except RuntimeError:
                pass
            new_next_post1 = Post.objects.get(id=next_post1.id)
            self.assertEquals(next_post1.sum_distance, new_next_post1.sum_distance)
            self.assertEquals(next_post1.status, new_next_post1.status)

    def test_update_next_posts(self):
        """Test that next posts will be updated"""
        self.create_post(Post.Status.SUCCESS, '0+10=10', 1)
        updated_post = self.create_post(Post.Status.ERROR_PARSE, 'text')
        changed_post = self.create_post(Post.Status.SUCCESS, '15+6=21', 3)

        with patch('app.services.sync_service._create_comment_text') as gi:
            sync_service.update_next_posts(updated_post)
            self.assertEqual(gi.call_count, 1)

        changed_post_new = Post.objects.get(id=changed_post.id)
        self.assertEqual(changed_post_new.status, Post.Status.ERROR_START_SUM)
        self.assertEqual(changed_post_new.number, 2)
        self.assertEqual(changed_post_new.sum_distance, 16)

    def test_update_next_posts_2(self):
        """Test that next posts will be updated"""
        self.create_post(Post.Status.SUCCESS, '0+10=10', 1)
        updated_post = self.create_post(Post.Status.SUCCESS, '10+5=15', 2)
        changed_post1 = self.create_post(Post.Status.SUCCESS, '15+6=21', 3)
        self.create_post(Post.Status.ERROR_PARSE, 'text')
        changed_post2 = self.create_post(Post.Status.SUCCESS, '21+3=24', 4)
        self.create_post(Post.Status.SUCCESS, '59+11=70', 5)

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
