import os
import tempfile
from unittest.mock import patch

from django.test import TestCase

from app.services import backup_service

GDRIVE_TEST_DIR_ID = '1G8cwWl1RyordtvcWqUR3Xn0ap0FTsVZx'


class BackupServiceTests(TestCase):

    @patch('django.core.management.call_command')
    @patch('app.services.backup_service._upload_file_to_gdrive')
    @patch('app.services.backup_service._delete_old_files')
    def test_backup_db_without_gdrive_folder_id(self, delete_old_files, upload_file_to_gdrive, call_command):
        with self.settings(GDRIVE_FOLDER_ID=None):
            result = backup_service.backup_db()
            self.assertIsNone(result)
            self.assertEquals(call_command.call_count, 0)
            self.assertEqual(upload_file_to_gdrive.call_count, 0)
            self.assertEqual(delete_old_files.call_count, 0)

    @patch('tempfile._mkstemp_inner')
    @patch('django.core.management.call_command')
    @patch('app.services.backup_service._upload_file_to_gdrive')
    @patch('app.services.backup_service._delete_old_files')
    def test_backup_db_with_fake_functions(self, delete_old_files, upload_file_to_gdrive, call_command, mkstemp):
        tmp_file_path = '/tmp/wildrace_test_db.json'
        tmp_file = os.open(tmp_file_path, tempfile._bin_openflags, 0o600)
        mkstemp.return_value = (tmp_file, tmp_file_path)

        backup_service.backup_db()
        self.assertEqual(mkstemp.call_count, 1)
        self.assertEqual(call_command.call_count, 1)
        self.assertEqual(call_command.call_args.args[0], 'dumpdata')
        self.assertEqual(call_command.call_args.kwargs, {'indent': 2, 'format': 'json', 'output': tmp_file_path})
        self.assertEqual(upload_file_to_gdrive.call_count, 1)
        self.assertEqual(upload_file_to_gdrive.call_args.args[0], tmp_file_path)
        self.assertFalse(os.path.exists(tmp_file_path))
        self.assertEqual(delete_old_files.call_count, 1)

    def test_backup_db(self):
        with self.settings(GDRIVE_FOLDER_ID=GDRIVE_TEST_DIR_ID, BACKUP_DB_FILE_NUMBER=0):
            res = backup_service.backup_db()
            self.assertIsInstance(res['id'], str)
            self.assertEquals(len(res['id']), 33)
