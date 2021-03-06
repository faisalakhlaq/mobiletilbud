# Generated by Django 3.1.3 on 2020-11-15 15:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mobileprice',
            options={'verbose_name': 'Mobile Price', 'verbose_name_plural': 'Mobile Prices'},
        ),
        migrations.AddField(
            model_name='mobileprice',
            name='mobile_variations',
            field=models.ManyToManyField(to='core.MobileVariation'),
        ),
        migrations.AddField(
            model_name='mobileprice',
            name='price_40_months',
            field=models.FloatField(blank=True, null=True, verbose_name='40 months price'),
        ),
        migrations.AddField(
            model_name='mobileprice',
            name='telecom_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.telecomcompany', verbose_name='Telecom Company'),
        ),
        migrations.AddField(
            model_name='mobiletechnicalspecification',
            name='ram',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='RAM'),
        ),
        migrations.AddField(
            model_name='package',
            name='for_young',
            field=models.BooleanField(default=False, verbose_name='For Young People'),
        ),
        migrations.AlterField(
            model_name='mobilecameraspecification',
            name='back_cam_aperture',
            field=models.CharField(max_length=30, verbose_name='Rear Camera Aperture'),
        ),
        migrations.AlterField(
            model_name='mobileprice',
            name='price_12_months',
            field=models.FloatField(blank=True, null=True, verbose_name='12 months price'),
        ),
        migrations.AlterField(
            model_name='mobileprice',
            name='price_24_months',
            field=models.FloatField(blank=True, null=True, verbose_name='24 months price'),
        ),
        migrations.AlterField(
            model_name='mobileprice',
            name='price_36_months',
            field=models.FloatField(blank=True, null=True, verbose_name='36 months price'),
        ),
        migrations.AlterField(
            model_name='mobileprice',
            name='price_6_months',
            field=models.FloatField(blank=True, null=True, verbose_name='6 months price'),
        ),
        migrations.AlterUniqueTogether(
            name='package',
            unique_together={('monthly_charges', 'telecom_company', 'for_young')},
        ),
    ]
