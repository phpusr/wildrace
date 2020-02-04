from django.test import TestCase

from app.services import sync_service


class SyncServiceTests(TestCase):

    def test_sync_posts(self):
        sync_service.sync_posts()
