import os
import tempfile
from unittest.mock import patch

from django.test import TestCase

from app.services import backup_service


class BackupServiceTests(TestCase):

    @patch('tempfile._mkstemp_inner')
    @patch('django.core.management.call_command')
    @patch('app.services.backup_service._upload_file_to_gdrive')
    @patch('app.services.backup_service._delete_old_files')
    def test_backup_db_with_fake_functions(self, delete_old_files, upload_file_to_gdrive, call_command, mock_tmp_file_name):
        tmp_file_path = '/tmp/wildrace_test_db.json'
        tmp_file = os.open(tmp_file_path, tempfile._bin_openflags, 0o600)
        mock_tmp_file_name.return_value = (tmp_file, tmp_file_path)

        backup_service.backup_db()
        self.assertEqual(mock_tmp_file_name.call_count, 1)
        self.assertEqual(call_command.call_count, 1)
        self.assertEqual(call_command.call_args.args[0], 'dumpdata')
        self.assertEqual(call_command.call_args.kwargs, {'indent': 2, 'format': 'json', 'output': tmp_file_path})
        self.assertEqual(upload_file_to_gdrive.call_count, 1)
        self.assertEqual(upload_file_to_gdrive.call_args.args[0], tmp_file_path)
        self.assertFalse(os.path.exists(tmp_file_path))
        self.assertEqual(delete_old_files.call_count, 1)

    def test_backup_db(self):
        result = backup_service.backup_db()
        self.assertIsInstance(result['id'], str)
        self.assertEquals(len(result['id']), 33)

    def test_delete_old_files(self):
        backup_service._delete_old_files()
