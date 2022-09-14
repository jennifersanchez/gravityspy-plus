# Generated by Django 4.0.4 on 2022-09-14 06:59

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classification_id', models.IntegerField()),
                ('annotation', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('workflow_id', models.IntegerField()),
                ('user_id', models.IntegerField()),
                ('subject_id', models.IntegerField()),
                ('event_time', models.FloatField()),
                ('gravityspy_id', models.CharField(max_length=30)),
                ('ifo', models.CharField(max_length=2)),
                ('main_channel_name', models.CharField(max_length=100)),
                ('event_generator', models.CharField(max_length=100)),
                ('annotation_channel_names', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None)),
                ('hveto_round_number', models.IntegerField()),
            ],
        ),
    ]
