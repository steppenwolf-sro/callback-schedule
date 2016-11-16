# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-16 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callback_schedule', '0002_auto_20161116_1927'),
        ('callback_request', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='callbackrequest',
            name='managers',
        ),
        migrations.RemoveField(
            model_name='callentry',
            name='succeeded',
        ),
        migrations.AddField(
            model_name='callbackrequest',
            name='phones',
            field=models.ManyToManyField(to='callback_schedule.CallbackManagerPhone'),
        ),
        migrations.AddField(
            model_name='callentry',
            name='state',
            field=models.CharField(choices=[('processing', 'Processing'), ('success', 'Success'), ('failed', 'Failed')], default='processing', max_length=32),
        ),
    ]
