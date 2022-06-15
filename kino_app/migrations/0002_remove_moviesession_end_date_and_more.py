# Generated by Django 4.0 on 2021-12-26 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kino_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='moviesession',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='moviesession',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='moviesession',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='moviesession',
            name='start_time',
        ),
        migrations.AddField(
            model_name='moviesession',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='moviesession',
            name='start_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
