import logging
import os
import tempfile
from datetime import datetime
from typing import Dict

from django.conf import settings
from django.core import management
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

BACKUP_DB_FORMAT = getattr(settings, 'BACKUP_DB_FORMAT', 'json')

logger = logging.getLogger(__name__)
service_account_file = os.path.join(settings.BASE_DIR, 'gdrive_account.json')
scopes = ['https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
service = build('drive', 'v3', credentials=credentials)


def backup_db():
    gdrive_dir_id = getattr(settings, 'GDRIVE_DIR_ID')
    if not gdrive_dir_id:
        logger.warning('Backup DB is disabled because "GDRIVE_DIR_ID" is not set')
        return

    with tempfile.NamedTemporaryFile() as tmp_file:
        management.call_command('dumpdata', indent=2, format=BACKUP_DB_FORMAT, output=tmp_file.name)
        result = _upload_file_to_gdrive(tmp_file.name)

    _delete_old_files()

    return result


def _upload_file_to_gdrive(file_path: str) -> Dict[str, str]:
    now_str = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    file_name = f'db_{now_str}.{BACKUP_DB_FORMAT}'
    file_metadata = {
        'name': file_name,
        'parents': [settings.GDRIVE_DIR_ID]
    }

    media = MediaFileUpload(file_path, resumable=True)
    result = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return result


def _delete_old_files():
    result = service.files().list(
        fields='files(id, name)',
        orderBy='name desc',
        pageSize=1000,
        q=f'"{settings.GDRIVE_DIR_ID}" in parents'
    ).execute()

    backup_db_file_number = getattr(settings, 'BACKUP_DB_FILE_NUMBER', 30)
    old_files = result['files'][backup_db_file_number:]
    for file in old_files:
        service.files().delete(fileId=file['id']).execute()
