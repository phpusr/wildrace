# Generated by Django 3.0.2 on 2020-01-30 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_profile_photo_max'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_sync',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
