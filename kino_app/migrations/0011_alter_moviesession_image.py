# Generated by Django 4.0.5 on 2022-06-22 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kino_app', '0010_alter_moviesession_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moviesession',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='posters/'),
        ),
    ]