# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-06 17:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20180503_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='customer',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.Customer'),
            preserve_default=False,
        ),
    ]