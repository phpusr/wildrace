from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Config(models.Model):
    sync_posts = models.BooleanField()
    """Post syncing"""

    sync_seconds = models.IntegerField()
    """Post syncing interval in seconds"""

    group_id = models.IntegerField()
    """VK group ID"""

    group_short_link = models.CharField(max_length=100)
    """VK group name in URL"""

    commenting = models.BooleanField()
    """Commenting of posts status processing"""

    comment_access_token = models.TextField(max_length=100)
    """Access token for comments"""

    comment_from_group = models.BooleanField()
    """Commenting by group name"""

    publish_stat = models.BooleanField()
    """Will it publish stat?"""

    @property
    def negative_group_id(self):
        return self.group_id * -1

    def __str__(self):
        return f'Config for: {self.group_short_link}'
