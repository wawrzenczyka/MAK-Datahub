# Generated by Django 2.2.6 on 2019-11-19 23:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('uploader', '0006_remove_datafile_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='datafile',
            name='file_type',
            field=models.CharField(default='S', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='datafile',
            name='file_uri',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='device',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]