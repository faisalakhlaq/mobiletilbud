# Generated by Django 3.1.3 on 2020-11-20 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telecompanies', '0003_offer_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='updated',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Updated'),
        ),
    ]
