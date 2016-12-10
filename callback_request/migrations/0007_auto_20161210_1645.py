# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-10 16:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('callback_request', '0006_auto_20161123_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='callbackrequest',
            name='error',
            field=models.CharField(blank=True, choices=[('no-answer', 'Client did not answer'), ('wrong-phone', 'Wrong phone number')], max_length=32),
        ),
        migrations.AlterField(
            model_name='callbackrequest',
            name='comment',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]