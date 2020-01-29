from django.contrib.auth import get_user_model
from django.test import TestCase

from app import models


class ModelTests(TestCase):
    def test_user_str(self):
        user = get_user_model().objects.create(username='phpusr')
        self.assertEquals(str(user), 'phpusr')
        self.assertEqual(user._meta.label, 'app.User')
