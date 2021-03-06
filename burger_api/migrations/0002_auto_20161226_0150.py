# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-25 23:50
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('burger_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='owner',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='time_to_deliver',
            field=models.DateTimeField(blank=True, validators=[django.core.validators.MinValueValidator(datetime.datetime(2016, 12, 25, 23, 50, 44, 897471, tzinfo=utc))]),
        ),
    ]
