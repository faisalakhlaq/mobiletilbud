# Generated by Django 3.1.3 on 2020-12-12 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobiles', '0019_auto_20201212_0247'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobiletechnicalspecification',
            name='status',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Status'),
        ),
    ]
