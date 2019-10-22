# Generated by Django 2.2.2 on 2019-10-22 18:23

import common.models
from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('search', '0009_auto_20190725_1728'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('locations', '0013_remove_location_addresses'),
    ]

    operations = [
        migrations.CreateModel(
            name='Algorithm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', common.models.RequiredURLField()),
                ('name', common.models.RequiredCharField(max_length=200)),
                ('notes', common.models.OptionalTextField()),
            ],
        ),
        migrations.CreateModel(
            name='SearchLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', common.models.OptionalTextField()),
                ('point', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='RelevancyScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
                ('time_stamp', models.DateTimeField()),
                ('algorithm', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='qa_tool.Algorithm')),
                ('search_location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='qa_tool.SearchLocation')),
                ('service_at_location', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='locations.ServiceAtLocation')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='search.Task')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
