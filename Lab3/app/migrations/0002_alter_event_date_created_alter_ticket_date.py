# Generated by Django 4.2.7 on 2024-10-23 01:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2024, 10, 23, 1, 31, 43, 357555, tzinfo=datetime.timezone.utc), verbose_name='Дата создания'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
