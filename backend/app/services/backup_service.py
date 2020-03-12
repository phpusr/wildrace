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


def backup_db():
    with tempfile.NamedTemporaryFile() as tmp_file:
        management.call_command('dumpdata', indent=2, format=BACKUP_DB_FORMAT, output=tmp_file.name)
        result = _upload_file_to_gdrive(tmp_file.name)
        return result


def _upload_file_to_gdrive(file_path: str) -> Dict[str, str]:
    now_str = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    file_name = f'db_{now_str}.{BACKUP_DB_FORMAT}'
    file_metadata = {
        'name': file_name,
        'parents': [settings.GDRIVE_DIR_ID]
    }

    service_account_file = os.path.join(settings.BASE_DIR, 'gdrive_account.json')
    scopes = ['https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('drive', 'v3', credentials=credentials)
    media = MediaFileUpload(file_path, resumable=True)
    result = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return result
