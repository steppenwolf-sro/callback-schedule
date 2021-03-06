# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-23 21:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('callback_schedule', '0002_auto_20161116_1927'),
        ('callback_request', '0005_auto_20161118_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='callentry',
            name='phones',
            field=models.ManyToManyField(related_name='phones', to='callback_schedule.CallbackManagerPhone'),
        ),
        migrations.AlterField(
            model_name='callbackrequest',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='callback_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='callentry',
            name='phone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='used_phones', to='callback_schedule.CallbackManagerPhone'),
        ),
    ]
