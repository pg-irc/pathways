# Generated by Django 2.2.4 on 2019-12-30 23:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('phone_at_location', '0003_auto_20180910_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phoneatlocation',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phone_numbers', to='locations.Location'),
        ),
    ]