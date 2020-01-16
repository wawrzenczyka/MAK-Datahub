# Generated by Django 2.2.6 on 2020-01-16 20:08

import core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('android_id', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileCreationRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('run_date', models.DateTimeField()),
                ('parsed_event_files', models.FileField(upload_to=core.models.ProfileCreationRun.generate_file_path)),
                ('unlock_data', models.FileField(upload_to=core.models.ProfileCreationRun.generate_file_path)),
                ('checkpoint_data', models.FileField(upload_to=core.models.ProfileCreationRun.generate_file_path)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_file', models.FileField(upload_to=core.models.ProfileInfo.generate_profile_path)),
                ('profile_type', models.CharField(choices=[(core.models.ProfileInfo.ProfileType('Unlock'), 'Unlock'), (core.models.ProfileInfo.ProfileType('Continuous'), 'Continuous')], max_length=20)),
                ('used_class_samples', models.IntegerField()),
                ('score', models.FloatField()),
                ('precision', models.FloatField()),
                ('recall', models.FloatField()),
                ('fscore', models.FloatField()),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Device')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProfileCreationRun')),
            ],
        ),
        migrations.CreateModel(
            name='DataFileInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.FileField(upload_to=core.models.DataFileInfo.generate_data_path)),
                ('start_date', models.DateTimeField()),
                ('file_type', models.CharField(choices=[(core.models.DataFileInfo.DataFileType('Event'), 'Event'), (core.models.DataFileInfo.DataFileType('Sensor'), 'Sensor')], max_length=20)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Device')),
            ],
        ),
    ]
