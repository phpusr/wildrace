from unittest.mock import patch

from django.test import TestCase

from app.tests import create_config
from tasks import tasks


class TaskTests(TestCase):

    def setUp(self):
        self.config = create_config()

    def test_sync_posts_task_is_disabled(self):
        res = tasks.sync_posts_task()
        self.assertEqual(res, 'Sync posts task is disabled')

    def test_sync_posts_task_is_worked(self):
        self.config.sync_posts = True
        self.config.save()
        with patch('app.services.sync_service.sync_posts') as sp:
            res = tasks.sync_posts_task()
            self.assertEqual(sp.call_count, 1)
            self.assertEqual(res, 'Sync posts task successfully finished')

    def test_publish_stat_task_is_disabled(self):
        res = tasks.publish_stat_task()
        self.assertEqual(res, 'Publish stat task is disabled')

    def test_publish_stat_task_is_worked(self):
        self.config.publish_stat = True
        self.config.save()
        with patch('app.services.stat_service.interval_publish_stat_post') as psp:
            res = tasks.publish_stat_task()
            self.assertEqual(psp.call_count, 1)
            self.assertEqual(res, 'Publish stat task successfully finished')

    def test_backup_db_is_disabled(self):
        with self.settings(GDRIVE_DIR_ID=None):
            res = tasks.backup_db_task()
            self.assertEqual(res, 'Backup DB task fail or disabled, see logs')

    @patch('django.core.management.call_command')
    @patch('app.services.backup_service._upload_file_to_gdrive')
    @patch('app.services.backup_service._delete_old_files')
    def test_backup_db_is_work(self, delete_old_files, upload_file_to_gdrive, call_command):
        result = {'id': 'hex777'}
        upload_file_to_gdrive.return_value = result
        res = tasks.backup_db_task()
        self.assertEqual(res, result)
