# Generated by Django 3.1.3 on 2020-11-15 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20201115_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobile',
            name='slug',
            field=models.SlugField(blank=True, null=True, verbose_name='slug'),
        ),
    ]