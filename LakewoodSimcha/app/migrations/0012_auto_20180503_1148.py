# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-03 15:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20180501_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='confirmed',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='venue',
            name='venue_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Wedding'), (2, 'Hall'), (3, 'Restaurant'), (4, 'Other')]),
        ),
    ]
