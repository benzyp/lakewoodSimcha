# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-03 19:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_venue_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='venue',
            name='duration',
            field=models.IntegerField(default=24),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venue',
            name='email',
            field=models.EmailField(default='benzyp@yahoo.com', max_length=254),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venue',
            name='phone',
            field=models.CharField(default='7329014412', max_length=10),
            preserve_default=False,
        ),
    ]
