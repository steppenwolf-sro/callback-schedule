# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-16 19:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callback_request', '0002_auto_20161116_1940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='callentry',
            name='manager_phone',
        ),
        migrations.AddField(
            model_name='callentry',
            name='attempt',
            field=models.IntegerField(default=0),
        ),
    ]
