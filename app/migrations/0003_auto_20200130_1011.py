# Generated by Django 3.0.2 on 2020-01-30 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_post'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='domain',
            field=models.SlugField(blank=True, max_length=100),
        ),
    ]
