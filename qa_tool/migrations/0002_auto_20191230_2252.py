# Generated by Django 2.2.4 on 2019-12-30 22:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qa_tool', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='algorithm',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='relevancyscore',
            options={'ordering': ['id']},
        ),
        migrations.AlterModelOptions(
            name='searchlocation',
            options={'ordering': ['id']},
        ),
    ]