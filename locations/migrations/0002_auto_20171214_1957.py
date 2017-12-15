# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-14 19:57
from __future__ import unicode_literals

import common.models
import django.core.validators
from django.db import migrations
import re


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='id',
            field=common.models.RequiredCharField(max_length=200, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z', 32), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')]),
        ),
    ]
