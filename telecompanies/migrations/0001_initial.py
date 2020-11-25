# Generated by Django 3.1.3 on 2020-11-17 00:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0007_auto_20201115_2123'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Mobile Name')),
                ('discount', models.CharField(blank=True, max_length=50, null=True, verbose_name='Discount')),
                ('offer_url', models.URLField(blank=True, max_length=300, null=True, verbose_name='Offer Url')),
                ('price', models.FloatField(blank=True, null=True, verbose_name='price')),
                ('slug', models.SlugField(blank=True, null=True, verbose_name='slug')),
                ('mobile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mobile', verbose_name='Mobile')),
                ('telecom_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.telecomcompany', verbose_name='Telecom Company')),
            ],
            options={
                'verbose_name': 'Offer',
                'verbose_name_plural': 'Offers',
            },
        ),
    ]