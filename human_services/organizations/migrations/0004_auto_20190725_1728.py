# Generated by Django 2.2.1 on 2019-07-25 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_auto_20180207_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationtranslation',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
