import os

import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .dev import *  # noqa: F401,F403

DEBUG = False

ALLOWED_HOSTS = ['*']

DB_URL = os.getenv('DATABASE_URL', 'postgres://127.0.0.1:5432/wildrace')
DATABASES = {
    'default': dj_database_url.parse(DB_URL)
}

sentry_sdk.init(
    dsn=os.getenv('SENTRY_BACKEND_DSN', ''),
    integrations=[DjangoIntegration()],
    send_default_pii=True
)
