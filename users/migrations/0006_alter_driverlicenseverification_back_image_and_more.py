# Generated by Django 5.2 on 2025-04-27 15:51

import users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_driverlicenseverification_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverlicenseverification',
            name='back_image',
            field=models.ImageField(upload_to=users.models.license_image_upload_path),
        ),
        migrations.AlterField(
            model_name='driverlicenseverification',
            name='front_image',
            field=models.ImageField(upload_to=users.models.license_image_upload_path),
        ),
        migrations.AlterField(
            model_name='driverlicenseverification',
            name='selfie_with_license',
            field=models.ImageField(upload_to=users.models.license_image_upload_path),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to=users.models.profile_picture_upload_path),
        ),
    ]
