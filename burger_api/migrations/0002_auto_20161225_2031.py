# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-25 18:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('burger_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='time_to_deliver',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4),
        ),
    ]
