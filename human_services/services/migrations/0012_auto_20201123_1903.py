# Generated by Django 3.1.2 on 2020-11-23 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0011_auto_20201118_2330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicetranslation',
            name='alternate_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='servicetranslation',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]
