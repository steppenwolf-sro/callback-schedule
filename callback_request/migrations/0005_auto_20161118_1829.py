# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-11-18 18:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('callback_schedule', '0002_auto_20161116_1927'),
        ('callback_request', '0004_auto_20161118_1205'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='callentry',
            name='uuid',
        ),
        migrations.AddField(
            model_name='callentry',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='callback_schedule.CallbackManager'),
        ),
        migrations.AlterField(
            model_name='callentry',
            name='phone',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='callback_schedule.CallbackManagerPhone'),
        ),
        migrations.AlterField(
            model_name='callentry',
            name='state',
            field=models.CharField(choices=[('waiting', 'Waiting'), ('direct', 'Direct'), ('canceled', 'Canceled'), ('success', 'Success'), ('failed', 'Failed'), ('no-answer', 'No answer')], default='waiting', max_length=32),
        ),
    ]
