import logging
import time
from datetime import datetime, timedelta
from hashlib import md5
from typing import List, Dict, Any

from django.utils import timezone

from app.enums import EventType
from app.models import Post, Profile
from app.services import vk_api_service

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

SYNC_BLOCK_INTERVAL = 1000
"""Interval between requests to vk in seconds"""

GETTING_USER_INTERVAL = 300
"""Interval between getting user info in seconds"""

PUBLISHING_COMMENT_INTERVAL = 300
"""Interval between comment publishing in seconds"""

logger = logging.getLogger(__name__)


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

    logger.debug('-------- End sync --------')


def _sync_block_posts(vk_post_count: int, download_count: int) -> int:
    db_post_count = Post.objects.count()
    logger.debug(f'>> Downloaded (before sync): {db_post_count}/{vk_post_count}')

    if vk_post_count - db_post_count > download_count:
        offset = vk_post_count - db_post_count - download_count
    else:
        offset = 0

    db_profiles = Profile.objects.all()

    response = vk_api_service.get_wall_posts(offset, download_count)

    if response['count'] != vk_post_count:
        logger.debug(f' -- Number of posts in VK changed: {vk_post_count} -> {response["count"]}')
        return db_post_count

    vk_posts = reversed(response['items'])

    last_db_posts = _get_last_posts(LAST_POSTS_COUNT)
    deleted_posts = _remove_deleted_posts(vk_posts, last_db_posts)

    for vk_post in vk_posts:
        post_id = vk_post['id']
        post_text = _remove_badh_chars(vk_post['text'])
        post_date = datetime.utcfromtimestamp(vk_post['date'])
        text_hash = md5(post_text)
        db_post = next(post for post in last_db_posts if post.id == post_id)
        last_post = _get_last_post(last_db_posts, post_id, post_date)
        last_sum_distance = last_post.sum_distance if last_post else 0
        last_post_number = last_post.number if last_post else 0

        if db_post:
            # if post exists in db and (it isn't modified or was hand modified) than continue to next post
            if text_hash == db_post.text_hash and db_post.start_sum == last_sum_distance \
                            or db_post.last_update is not None:
                continue

            _analyze_post_text(post_text, text_hash, last_sum_distance, last_post_number, db_post, EventType.Update)
            continue

        # Searching and creating a new profile
        profile = _find_or_create_profile(vk_post, post_date, db_profiles)
        new_post = Post(id=post_id, status=Post.Status.SUCCESS, profile=profile, date=post_date)

        parser_out = _analyze_post_text(post_text, text_hash, last_sum_distance, last_post_number, new_post,
                                        EventType.Create)

        # Adding a new post into last posts and post sorting by time
        if paser_out:
            last_db_posts.append(new_post)
            last_db_posts.sort(key=lambda post: post.date, reverse=True)

    return Post.objects.count()


def _get_last_posts(post_count: int) -> List[Post]:
    return Post.objects.all().order_by('-date')[:post_count]


def _remove_deleted_posts(vk_posts: List[dict], last_db_posts: List[Post]) -> List[Post]:
    """Deleting from DB deleted posts"""
    # Searching posts for last {number_of_last_days}
    number_of_last_days = 5
    start_date = timezone.now() - timedelta(days=number_of_last_days)
    last_day_posts = [post for post in last_db_posts if post.date >= start_date]

    def not_find_in_vk(post_id):
        res = [post for post in vk_posts if post['i'] == post_id]
        return len(res) == 0
    deleted_posts = [post for post in last_day_posts if not_find_in_vk(post.id)]

    if not deleted_posts:
        return deleted_posts

    logger.debug(f'>> Delete vk_posts, number: {len(deleted_posts)}')
    for post in deleted_posts:
        logger.debug(f' -- Delete {post}')
        post.delete()
        last_db_posts.remove(post)

    return deleted_posts


def _get_last_post(posts, post_id, post_date):
    filter_posts = [post for post in posts if post.number is not None
                    and post.id != post_id
                    and post.date <= post_date]
    if len(filter_posts):
        return filter_posts[0]
