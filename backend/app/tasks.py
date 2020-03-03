import logging

from app.celery import app
from app.models import Config
from app.services import sync_service, stat_service

logger = logging.getLogger(__name__)


@app.task
def sync_posts_task():
    logger.info('-- Sync posts task started --')

    if not Config.objects.get().sync_posts:
        msg = 'Sync posts task is disabled'
        logger.info(f'>> {msg}')
        return msg

    sync_service.sync_posts()

    msg = 'Sync posts task successfully finished'
    logger.info(f'-- {msg} --')
    return msg


@app.task
def publish_stat_task():
    logger.info('-- Publish stat task started')

    if not Config.objects.get().publish_stat:
        msg = 'Publish stat task is disabled'
        logger.info(f'>> {msg}')
        return msg

    stat_service.interval_publish_stat_post()

    msg = 'Publish stat task successfully finished'
    logger.info(f'-- {msg} --')
    return msg
