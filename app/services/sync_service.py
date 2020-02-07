import logging
import time
from datetime import datetime, timedelta
from hashlib import md5
from typing import List, Iterator

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from app.enums import EventType
from app.models import Post, Profile, Config
from app.services import vk_api_service, message_parser, stat_service
from app.util import find, find_all, remove_non_utf8_chars

DOWNLOAD_POST_COUNT = 100
"""
Downloading post count for one time.
Post changes fix only in last 100
"""

LAST_POSTS_COUNT = DOWNLOAD_POST_COUNT * 2
"""
Post count for searching last data.
Some posts may change or delete
"""

SYNC_BLOCK_INTERVAL = 1
"""Interval between requests to vk in seconds"""

GETTING_USER_INTERVAL = 0.3
"""Interval between getting user info in seconds"""

PUBLISHING_COMMENT_INTERVAL = 0.3
"""Interval between comment publishing in seconds"""

logger = logging.getLogger(__name__)


@transaction.atomic
def sync_posts():
    logger.debug('-------- Start sync --------')

    need_sync = True
    while need_sync:
        vk_post_count = vk_api_service.get_wall_posts(0, 1)['count']
        db_post_count = _sync_block_posts(vk_post_count, DOWNLOAD_POST_COUNT)
        logger.debug(f'>> Downloaded (after sync): {db_post_count}/{vk_post_count}')

        if db_post_count > vk_post_count:
            raise RuntimeError(f'Number of posts in DB ({db_post_count}) > number of posts in VK ({vk_post_count})')

        need_sync = db_post_count < vk_post_count

        if need_sync:
            time.sleep(SYNC_BLOCK_INTERVAL)

    stat_service.update_stat()

    logger.debug('-------- End sync --------')


def _sync_block_posts(vk_post_count: int, download_count: int) -> int:
    db_post_count = Post.objects.count()
    logger.debug(f'>> Downloaded (before sync): {db_post_count}/{vk_post_count}')

    if vk_post_count - db_post_count > download_count:
        offset = vk_post_count - db_post_count - download_count
    else:
        offset = 0

    db_profiles = list(Profile.objects.all())

    response = vk_api_service.get_wall_posts(offset, download_count)

    if response['count'] != vk_post_count:
        logger.debug(f' -- Number of posts in VK changed: {vk_post_count} -> {response["count"]}')
        return db_post_count

    vk_posts = list(reversed(response['items']))

    last_db_posts = _get_last_posts(LAST_POSTS_COUNT)
    _remove_deleted_posts(vk_posts, last_db_posts)

    for vk_post in vk_posts:
        post_id = vk_post['id']
        post_text = remove_non_utf8_chars(vk_post['text'])
        post_date = datetime.utcfromtimestamp(vk_post['date']).astimezone(timezone.get_default_timezone())
        text_hash = md5(post_text.encode()).hexdigest()
        db_post = find(last_db_posts, lambda it: it.id == post_id)
        last_post = _get_last_post(last_db_posts, post_id, post_date)
        last_sum_distance = last_post.sum_distance if last_post else 0
        last_post_number = last_post.number if last_post else 0

        if db_post:
            # if post exists in db and (it isn't modified or was hand modified) than continue to next post
            if text_hash == db_post.text_hash and db_post.start_sum == last_sum_distance \
                            or db_post.last_update is not None:
                continue

            _analyze_post_text(post_text, text_hash, last_sum_distance, last_post_number, db_post, EventType.UPDATE)
            continue

        # Searching and creating a new profile
        profile = _find_or_create_profile(vk_post, post_date, db_profiles)
        new_post = Post(id=post_id, status=Post.Status.SUCCESS, author=profile, date=post_date)

        parser_out = _analyze_post_text(post_text, text_hash, last_sum_distance, last_post_number, new_post,
                                        EventType.CREATE)

        # Adding a new post into last posts and post sorting by time
        if parser_out:
            last_db_posts.append(new_post)
            last_db_posts.sort(key=lambda post: post.date, reverse=True)

    return Post.objects.count()


def _get_last_posts(post_count: int) -> List[Post]:
    return list(Post.objects.all().order_by('-date')[:post_count])


def _remove_deleted_posts(vk_posts: Iterator[dict], last_db_posts: List[Post]) -> List[Post]:
    """Deleting from DB deleted posts"""
    # Searching posts for last {number_of_last_days}
    number_of_last_days = 5
    start_date = timezone.now() - timedelta(days=number_of_last_days)
    last_day_posts = [post for post in last_db_posts if post.date >= start_date]

    def not_find_in_vk(post):
        return find(vk_posts, lambda it: it['id'] == post.id) is None

    deleted_posts = find_all(last_day_posts, not_find_in_vk)

    if not deleted_posts:
        return deleted_posts

    logger.debug(f'>> Delete vk_posts, number: {len(deleted_posts)}')
    for post in deleted_posts:
        logger.debug(f' -- Delete {post}')
        post.delete()
        last_db_posts.remove(post)

    return deleted_posts


def _get_last_post(posts, post_id, post_date):
    return find(posts, lambda it: it.number is not None and it.id != post_id and it.date <= post_date)


def _find_or_create_profile(vk_post: dict, post_date: datetime, db_profiles: List[Profile]) -> Profile:
    profile_id = vk_post['from_id']
    db_profile = find(db_profiles, lambda it: it.id == profile_id)
    if db_profile:
        return db_profile

    db_profile = Profile(id=profile_id, join_date=post_date, first_name='Unknown', sex=Profile.Sex.UNKNOWN)
    time.sleep(GETTING_USER_INTERVAL)

    if profile_id >= 0:
        vk_user = vk_api_service.get_user(profile_id)
        if vk_user:
            db_profile.first_name = vk_user['first_name']
            db_profile.last_name = vk_user['last_name']
            db_profile.sex = vk_user['sex']
            db_profile.photo_50 = vk_user['photo_50']
            db_profile.photo_100 = vk_user['photo_100']
    else:
        vk_group = vk_api_service.get_group(profile_id * -1)
        if vk_group:
            db_profile.first_name = vk_group['name']
            db_profile.photo_50 = vk_group['photo_50']
            db_profile.photo_100 = vk_group['photo_100']
            db_profile.photo_200 = vk_group['photo_200']

    db_profile.save()
    db_profiles.append(db_profile)

    return db_profile


def _analyze_post_text(text: str, text_hash: str, last_sum_distance: int, last_post_number: int, post: Post,
                       event_type: EventType) -> bool:
    parser_out = message_parser.parse(text)

    post.text = text
    post.text_hash = text_hash
    if parser_out:
        distance = parser_out.distance
        new_sum_distance = last_sum_distance + distance

        if parser_out.start_sum_number == last_sum_distance:
            if new_sum_distance == parser_out.end_sum_number:
                status = Post.Status.SUCCESS
            else:
                status = Post.Status.ERROR_SUM
        else:
            status = Post.Status.ERROR_START_SUM

        number = last_post_number + 1
    else:
        status = Post.Status.ERROR_PARSE
        number = None
        distance = None
        new_sum_distance = None

    # Check that sum expression is changed
    if (post.number != number
            or post.distance != distance
            or post.sum_distance != new_sum_distance
            or post.status != status):

        post.number = number
        post.distance = distance
        post.sum_distance = new_sum_distance
        post.status = status

        post.save()
        logger.debug(f' -- {event_type.name} post after analyze: {post}')

        # Adding status comment for post
        comment_text = _create_comment_text(post, last_sum_distance, new_sum_distance)
        _add_status_comment(post.id, comment_text)

    return parser_out is not None


def _create_comment_text(post: Post, start_sum_distance: int, end_sum_distance: int) -> str:
    comment_text = ''

    # Appeal
    if post.status != Post.Status.SUCCESS:
        if post.author.id > 0:
            comment_text += f'@id{post.author.id} ({post.author.first_name}), '
        else:
            comment_text += f'@club{post.author.id * -1} ({post.author.first_name}), '

    # Running number
    if post.status != Post.Status.ERROR_PARSE:
        comment_text += f'#{post.number} пробежка: '

    comment_text += {
        Post.Status.SUCCESS: 'Пост успешно обработан',
        Post.Status.ERROR_SUM: f'Ошибка при сложении, должно быть: {end_sum_distance}',
        Post.Status.ERROR_PARSE: f'Ошибка в формате записи, пост не распознан',
        Post.Status.ERROR_START_SUM: f'Ошибка в стартовой сумме, должна быть: {start_sum_distance}'
    }.get(post.status, 'Ошибка: Не предусмотренный статус, напишите администратору')

    return comment_text


def _add_status_comment(post_id: int, comment_text: str):
    if not Config.objects.get().commenting:
        return

    time.sleep(PUBLISHING_COMMENT_INTERVAL)
    vk_api_service.add_comment_to_post(post_id, comment_text)


@transaction.atomic
def update_next_posts(updated_post: Post):
    if updated_post.number is not None:
        start_post = updated_post
    else:
        start_post = Post.runnings.filter(date__lte=updated_post.date).order_by('-date').first()

    logger.debug(f'> Update next, start: {start_post}')

    current_post_number = start_post.number if start_post else 0
    current_sum_distance = start_post.sum_distance if start_post else 0

    next_posts = Post.runnings.filter(date__gte=updated_post.date).order_by('date')
    if start_post is not None:
        next_posts = next_posts.filter(~Q(id=start_post.id) & Q(date__gte=start_post.date))

    for post in next_posts:
        _analyze_post_text(post.text, post.text_hash, current_sum_distance, current_post_number, post,
                           EventType.UPDATE)
        current_sum_distance = post.sum_distance
        current_post_number = post.number
