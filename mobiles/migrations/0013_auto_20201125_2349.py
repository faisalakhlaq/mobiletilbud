# Generated by Django 3.1.3 on 2020-11-25 22:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobiles', '0012_auto_20201125_0228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobilecameraspecification',
            name='front_cam_megapixel',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='front_camera_megapixel'),
        ),
        migrations.AlterField(
            model_name='mobilecameraspecification',
            name='rear_cam_megapixel',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='rear_camera_megapixel'),
        ),
    ]
