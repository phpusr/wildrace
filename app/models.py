from django.conf import settings
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
        return f'Config for: {self.group_id}'


class Profile(models.Model):
    join_date = models.DateTimeField()
    """First running date - join date"""

    last_sync = models.DateTimeField(null=True, blank=True)
    """Last sync date"""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Sex(models.IntegerChoices):
        UNKNOWN = 0
        FEMALE = 1
        MALE = 2

    sex = models.IntegerField(choices=Sex.choices)

    birth_date = models.CharField(max_length=10, blank=True)
    """
    Дата рождения. Возвращается в формате DD.MM.YYYY или DD.MM (если год рождения скрыт).
    Если дата рождения скрыта целиком, поле отсутствует в ответе
    """

    city = models.CharField(max_length=100, blank=True)

    country = models.CharField(max_length=100, blank=True)

    has_photo = models.BooleanField(null=True, blank=True)

    photo_50 = models.URLField(blank=True)
    """
    url квадратной фотографии пользователя, имеющей ширину 50 пикселей.
    В случае отсутствия у пользователя фотографии возвращается http://vk.com/images/camera_c.gif
    """

    photo_100 = models.URLField(blank=True)
    """
    url квадратной фотографии пользователя, имеющей ширину 100 пикселей.
    В случае отсутствия у пользователя фотографии возвращается http://vk.com/images/camera_b.gif
    """

    photo_200 = models.URLField(blank=True)
    """
    url квадратной фотографии пользователя, имеющей ширину 200 пикселей.
    Если фотография была загружена давно, изображения с такими размерами может не быть,
    в этом случае ответ не будет содержать этого поля
    """

    photo_200_orig = models.URLField(blank=True)
    """
    url фотографии пользователя, имеющей ширину 200 пикселей.
    В случае отсутствия у пользователя фотографии возвращается http://vk.com/images/camera_a.gif
    """

    photo_400_orig = models.URLField(blank=True)
    """
    url фотографии пользователя, имеющей ширину 400 пикселей.
    Если у пользователя отсутствует фотография такого размера, ответ не будет содержать этого поля
    """

    photo_max = models.URLField(blank=True)
    """
    url квадратной фотографии пользователя с максимальной шириной.
    Может быть возвращена фотография, имеющая ширину как 200, так и 100 пикселей.
    В случае отсутствия у пользователя фотографии возвращается http://vk.com/images/camera_b.gif
    """

    photo_max_orig = models.URLField(blank=True)
    """
    url фотографии пользователя максимального размера.
    Может быть возвращена фотография, имеющая ширину как 400, так и 200 пикселей.
    В случае отсутствия у пользователя фотографии возвращается http://vk.com/images/camera_a.gif
    """

    domain = models.SlugField(max_length=100, blank=True)

    @property
    def first_and_last_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def vk_link(self):
        return f'{settings.VK_LINK}/id{self.id}'

    def get_vk_link_for_post(self, is_development_env):
        return self.first_and_last_name if is_development_env else f'@id{self.id} ({self.first_and_last_name})'

    def __str__(self):
        return self.first_and_last_name


class RunningManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(number__isnull=False)


class Post(models.Model):
    class Status(models.IntegerChoices):
        SUCCESS = 1
        ERROR_SUM = 2
        ERROR_PARSE = 3
        ERROR_START_SUM = 4

    status = models.IntegerField(choices=Status.choices)
    """Post processing status"""

    author = models.ForeignKey(to=Profile, on_delete=models.PROTECT)

    date = models.DateTimeField()

    number = models.IntegerField(null=True, blank=True)

    text = models.TextField()

    text_hash = models.CharField(max_length=32)

    distance = models.IntegerField(null=True, blank=True)

    sum_distance = models.IntegerField(null=True, blank=True)

    edit_reason = models.CharField(max_length=255, null=True, blank=True)

    last_update = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    runnings = RunningManager()

    @property
    def start_sum(self):
        if self.sum_distance is not None and self.distance is not None:
            return self.sum_distance - self.distance

    def __str__(self):
        return f'Post(id: {self.id}, number: {self.number}, text: {self.text})'


class StatLog(models.Model):
    publish_date = models.DateTimeField()

    class StatType(models.IntegerChoices):
        DISTANCE = 0
        DATE = 1

    stat_type = models.IntegerField(choices=StatType.choices)

    start_value = models.CharField(max_length=100)

    end_value = models.CharField(max_length=100)

    post_id = models.IntegerField()

    def __str__(self):
        return f'StatLog({self.start_value} - {self.end_value})'


class TempData(models.Model):
    last_sync_date = models.DateTimeField()

    def __str__(self):
        return self.__class__.__name__
