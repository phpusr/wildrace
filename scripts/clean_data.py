import os

import django


def delete_all_objects(model):
    objects = model.objects.all()
    count = objects.count()
    objects.delete()
    print(f' - Deleted {count} objects from {model.__name__}')


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    django.setup()
    from app import models  # noqa: E402

    print('Clean data')
    delete_all_objects(models.Post)
    delete_all_objects(models.Profile)
    delete_all_objects(models.StatLog)
