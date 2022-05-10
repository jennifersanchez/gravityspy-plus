# Generated by Django 4.0.4 on 2022-05-06 18:46

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GravitySpySubject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_time', models.FloatField()),
                ('gravityspy_id', models.CharField(max_length=30)),
                ('ifo', models.CharField(max_length=2)),
                ('main_channel', models.CharField(max_length=100)),
                ('event_generator', models.CharField(max_length=100)),
                ('q_values', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None)),
                ('list_of_auxiliary_channel_names', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None)),
                ('zooniverse_subject_ids', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
            ],
        ),
    ]
