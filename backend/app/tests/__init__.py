import os
from datetime import datetime
from hashlib import md5

from django.utils import timezone

from app import models
from app.models import Profile, Post
from app.services import sync_service, message_parser


def create_admin():
    return models.User.objects.get(username='phpusr')


def create_config():
    models.Config.objects.all().update(
        sync_posts=False,
        group_id=88923650,
        commenting=False,
        comment_access_token=os.getenv('VK_ACCESS_TOKEN'),
        comment_from_group=False,
        publish_stat=False
    )
    return models.Config.objects.get()


def create_profile():
    return models.Profile.objects.create(
        join_date=timezone.now(),
        last_sync=timezone.now(),
        first_name='Ivan',
        last_name='Fuckoff',
        sex=models.Profile.Sex.UNKNOWN
    )


def create_vk_post(post_id, profile_id, text, timestamp=None):
    return {
        'id': post_id,
        'from_id': profile_id,
        'text': text,
        'date': timestamp if timestamp else round(timezone.now().timestamp())
    }


def create_post(status, profile, text, number=None, post_id=None, date=None,
                timestamp=None):
    out = message_parser.parse(text)

    if not date:
        if timestamp:
            date = datetime.utcfromtimestamp(timestamp).astimezone(timezone.get_default_timezone())
        else:
            date = timezone.now()

    return Post.objects.create(
        id=post_id,
        author=profile,
        status=status,
        date=date,
        text=text,
        text_hash=md5(text.encode()).hexdigest(),
        number=number,
        distance=out.distance if out else None,
        sum_distance=out.end_sum_number if out else None
    )


def create_stat_log():
    return models.StatLog.objects.create(
        publish_date=timezone.now(),
        stat_type=models.StatLog.StatType.DATE,
        post_id=1,
        start_value='10.01.2020',
        end_value='15.02.2020'
    )


def create_temp_data():
    return models.TempData.objects.get()


def create_or_get_profile(profile_id, first_name, last_name, date):
    profile = Profile.objects.filter(pk=profile_id).first()
    if profile:
        return profile

    return Profile.objects.create(
        pk=profile_id,
        first_name=first_name,
        last_name=last_name,
        join_date=date,
        sex=Profile.Sex.MALE
    )


def create_running(number, profile, distance, sum_distance, date):
    if not distance:
        status = Post.Status.ERROR_PARSE
        number = None
        sum_distance = None
    else:
        status = Post.Status.SUCCESS

    return Post.objects.create(
        status=status,
        number=number,
        author=profile,
        distance=distance,
        sum_distance=sum_distance,
        date=date,
        text=f'+{distance}={sum_distance}'
    )


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


def create_runnings():
    number = 0
    sum_distance = 0
    runnings = []

    with open(os.path.join(TESTS_DIR, 'data', 'runnings.txt')) as f:
        for row in f.readlines():
            if not row:
                continue

            props = row.split('|')
            date = datetime.strptime(props[0].strip(), '%Y-%m-%d %H:%M:%S') \
                .astimezone(timezone.get_default_timezone())
            profile_id = int(props[1].strip())
            first_name = props[2].strip()
            last_name = props[3].strip()
            try:
                distance = int(props[4].strip())
                sum_distance += distance
                number += 1
            except ValueError:
                distance = None

            profile = create_or_get_profile(profile_id, first_name, last_name, date)
            running = create_running(number, profile, distance, sum_distance, date)
            runnings.append(running)
        return runnings


def create_date(year, month, day, hour=0, minute=0, second=0):
    return datetime(year, month, day, hour, minute, second).astimezone(timezone.get_current_timezone())


def create_comment_text(status, profile=None):
    if not profile:
        profile = Profile(id=347, first_name='Иван')
    post = Post(status=status, number=22, author=profile)
    return sync_service._create_comment_text(post, 10, 20)
