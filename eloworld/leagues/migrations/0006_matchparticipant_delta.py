# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-22 14:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leagues', '0005_league_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchparticipant',
            name='delta',
            field=models.IntegerField(default=0),
        ),
    ]
