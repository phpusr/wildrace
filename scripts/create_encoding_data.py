import json
import os

import django
from django.conf import settings
from django.core import signing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()


def encode():
    file_path = os.path.join(settings.BASE_DIR, 'gdrive_account.json')
    data = json.load(open(file_path))
    value = signing.dumps(data, compress=True)
    print(value)
    print('size:', len(value))


def decode():
    file_path = os.path.join(settings.BASE_DIR, 'gdrive_account.enc')
    data = open(file_path).read()
    value = signing.loads(data)
    print(value)


if __name__ == '__main__':
    encode()
    decode()
