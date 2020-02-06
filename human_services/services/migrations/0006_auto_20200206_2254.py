# Generated by Django 3.0.2 on 2020-02-06 22:54

import common.models
import django.core.validators
from django.db import migrations
import django.db.models.deletion
import parler.fields
import re


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_auto_20180910_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='id',
            field=common.models.RequiredCharField(max_length=200, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')]),
        ),
        migrations.AlterField(
            model_name='servicetranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='services.Service'),
        ),
    ]
