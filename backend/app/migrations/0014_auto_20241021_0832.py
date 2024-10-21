# Generated by Django 3.0.14 on 2024-10-21 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20221015_1245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='photo_100',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='profile',
            name='photo_200',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='profile',
            name='photo_200_orig',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='profile',
            name='photo_400_orig',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='profile',
            name='photo_50',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='profile',
            name='photo_max',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='profile',
            name='photo_max_orig',
            field=models.URLField(blank=True, max_length=500),
        ),
    ]
