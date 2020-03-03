import logging

from app.celery import app
from app.models import Config
from app.services import sync_service, stat_service

logger = logging.getLogger(__name__)


@app.task
def sync_posts_task():
    logger.info('-- Sync posts job started --')

    if not Config.objects.get().sync_posts:
        logger.info('>> Sync posts task is disabled')
        return

    sync_service.sync_posts()

    logger.info('-- Sync posts task finished --')


@app.task
def stat_publish_task():
    logger.info('-- Stat publish task started')

    if not Config.objects.get().publish_stat:
        logger.info('>> Publish task is disabled')

    stat_service.publish_stat_post()

    logger.info('Stat publish task finished')
