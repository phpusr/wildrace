from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'sync-posts-task': {
        'task': 'app.tasks.sync_posts_task',
        'schedule': crontab(minute='*/5')
    },
    'publish-stat-task': {
        'task': 'app.tasks.publish_stat_task',
        'schedule': crontab(minute=0)
    }
}
