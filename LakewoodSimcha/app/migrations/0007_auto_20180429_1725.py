# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-29 21:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20180429_1631'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='name',
            new_name='title',
        ),
    ]