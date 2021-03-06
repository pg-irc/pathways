# Generated by Django 3.1.2 on 2021-01-07 19:44

import common.models
import django.core.validators
from django.db import migrations
import re
import taxonomies.models


class Migration(migrations.Migration):

    dependencies = [
        ('taxonomies', '0007_auto_20201230_2208'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taxonomyterm',
            name='taxonomy_term_id',
        ),
        migrations.AlterField(
            model_name='taxonomyterm',
            name='id',
            field=common.models.RequiredCharField(default=taxonomies.models.default_term_id, max_length=200, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), 'Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.', 'invalid')]),
        ),
    ]
