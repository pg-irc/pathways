# Generated by Django 3.1.2 on 2020-10-27 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0008_merge_20200706_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicetranslation',
            name='alternate_name',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
