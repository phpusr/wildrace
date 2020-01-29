from django.db import models


class PhotoURLField(models.URLField):
    """url фотографии пользователя"""
    max_length = 255
