# Generated by Django 3.1.3 on 2020-11-23 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobiles', '0004_auto_20201123_0232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mobile',
            name='name',
            field=models.CharField(max_length=50, verbose_name='name'),
        ),
        migrations.AlterUniqueTogether(
            name='mobile',
            unique_together={('name', 'brand')},
        ),
    ]
