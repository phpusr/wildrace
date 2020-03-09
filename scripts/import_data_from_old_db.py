import os
from sys import getsizeof

import django
import psycopg2
import pytz
from psycopg2.extras import RealDictCursor

from scripts.clean_data import delete_all_objects


def execute(table_name):
    cursor.execute(f'SELECT * FROM {table_name}')
    results = cursor.fetchall()

    size = round(getsizeof(results) / 1024, 2)
    print(f'Imported from "{table_name}"')
    print(f' - Count: {len(results)}')
    print(f' - Size: {size} KB')
    return results


def get_value_or_empty_string(value):
    return value if value is not None else ''


def get_date(value):
    return value.astimezone(pytz.UTC) if value else None


def import_config():
    results = execute('config')
    for row in results:
        models.Config.objects.create(
            id=row['id'],
            sync_posts=row['sync_posts'],
            group_id=row['group_id'],
            commenting=row['commenting'],
            comment_access_token=row['comment_access_token'],
            comment_from_group=row['comment_from_group'],
            publish_stat=row['publish_stat'],
        )


def import_profiles():
    results = execute('profile')
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


def import_posts():
    results = execute('post')
    for row in results:
        models.Post.objects.create(
            status=row['status'],
            author_id=row['from_id'],
            date=get_date(row['date']),
            number=row['number'],
            text=row['text'],
            text_hash=row['text_hash'],
            distance=row['distance'],
            sum_distance=row['sum_distance'],
            edit_reason=row['edit_reason'],
            last_update=get_date(row['last_update']),
        )


def import_stat_logs():
    results = execute('stat_log')
    for row in results:
        models.StatLog.objects.create(
            id=row['id'],
            publish_date=get_date(row['publish_date']),
            stat_type=row['stat_type'],
            start_value=row['start_value'],
            end_value=row['end_value'],
            post_id=row['post_id']
        )


def import_temp_data():
    results = execute('temp_data')
    for row in results:
        models.TempData.objects.create(id=row['id'], last_sync_date=get_date(row['last_sync_date']))


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    django.setup()
    from app import models  # noqa: E402

    with psycopg2.connect(host='127.0.0.1', user='phpusr', dbname='wildrace_v2', cursor_factory=RealDictCursor) as conn:
        if True:
            print('Clean DB')
            delete_all_objects(models.Config)
            delete_all_objects(models.Post)
            delete_all_objects(models.Profile)
            delete_all_objects(models.StatLog)
            delete_all_objects(models.TempData)

        cursor = conn.cursor()
        import_config()
        import_profiles()
        import_posts()
        import_stat_logs()
        import_temp_data()
