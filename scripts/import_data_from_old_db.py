import os
from sys import getsizeof

import django
import psycopg2
import pytz
from psycopg2.extras import RealDictCursor


def execute(sql):
    cursor.execute(sql)
    results = cursor.fetchall()
    size = round(getsizeof(results) / 1024, 2)
    print(f'Count: {len(results)}')
    print(f'Size: {size} KB')
    return results


def get_value_or_empty_string(value):
    return value if value is not None else ''


def get_date(value):
    return value.astimezone(pytz.UTC) if value else None


def import_config():
    results = execute('select * from config')
    for row in results:
        models.Config.objects.create(
            id=row['id'],
            sync_posts=row['sync_posts'],
            sync_seconds=row['sync_seconds'],
            group_id=row['group_id'],
            group_short_link=row['group_short_link'],
            commenting=row['commenting'],
            comment_access_token=row['comment_access_token'],
            comment_from_group=row['comment_from_group'],
            publish_stat=row['publish_stat'],
        )


def import_profiles():
    results = execute('select * from profile')
    for row in results:
        models.Profile.objects.create(
            id=row['id'],
            join_date=get_date(row['join_date']),
            last_sync=get_date(row['last_sync']),
            first_name=row['first_name'],
            last_name=row['last_name'],
            sex=row['sex'] if row['sex'] else models.Profile.Sex.UNKNOWN,
            birth_date=get_value_or_empty_string(row['birth_date']),
            city=get_value_or_empty_string(row['city']),
            country=get_value_or_empty_string(row['country']),
            has_photo=row['has_photo'],
            photo_50=get_value_or_empty_string(row['photo_50']),
            photo_100=get_value_or_empty_string(row['photo_100']),
            photo_200=get_value_or_empty_string(row['photo_200']),
            photo_200_orig=get_value_or_empty_string(row['photo_200_orig']),
            photo_400_orig=get_value_or_empty_string(row['photo_400_orig']),
            photo_max=get_value_or_empty_string(row['photo_max']),
            photo_max_orig=get_value_or_empty_string(row['photo_max_orig']),
            domain=get_value_or_empty_string(row['domain'])
        )


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()
from app import models  # noqa: E402

with psycopg2.connect(host='127.0.0.1', user='phpusr', dbname='wildrace', cursor_factory=RealDictCursor) as conn:
    cursor = conn.cursor()
    # import_config()
    # import_profiles()
