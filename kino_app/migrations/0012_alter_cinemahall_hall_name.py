# Generated by Django 4.0.5 on 2022-06-26 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kino_app', '0011_alter_moviesession_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cinemahall',
            name='hall_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
