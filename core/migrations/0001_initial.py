# Generated by Django 3.1.3 on 2020-11-15 05:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mobile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('cash_price', models.FloatField(blank=True, null=True, verbose_name='Cash Price')),
                ('slug', models.SlugField(verbose_name='slug')),
            ],
        ),
        migrations.CreateModel(
            name='MobileBrand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='TelecomCompany',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('slug', models.SlugField(verbose_name='slug')),
            ],
            options={
                'verbose_name': 'Telecom Company',
                'verbose_name_plural': 'Telecom Companies',
            },
        ),
        migrations.CreateModel(
            name='Variation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('mobile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mobile')),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('monthly_charges', models.FloatField(verbose_name='Monthly Charges')),
                ('mobile_data', models.CharField(blank=True, max_length=50, null=True, verbose_name='Mobile Data')),
                ('data_in_other_countries', models.CharField(blank=True, max_length=50, null=True, verbose_name='Data in other countries')),
                ('telecom_company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.telecomcompany', verbose_name='Telecom Company')),
            ],
            options={
                'verbose_name': 'Package',
                'verbose_name_plural': 'Packages',
            },
        ),
        migrations.CreateModel(
            name='MobileTechnicalSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('two_g', models.BooleanField()),
                ('three_g', models.BooleanField()),
                ('four_g', models.BooleanField()),
                ('five_g', models.BooleanField()),
                ('WiFi', models.BooleanField()),
                ('taleVoLTE', models.BooleanField()),
                ('dual_sim', models.BooleanField()),
                ('dimensions', models.CharField(max_length=50, verbose_name='dimensions')),
                ('weight', models.CharField(max_length=10, verbose_name='weight')),
                ('screen_type', models.CharField(max_length=50, verbose_name='screen_type')),
                ('screen_size', models.CharField(max_length=10, verbose_name='screen_size')),
                ('screen_resolution', models.CharField(max_length=30, verbose_name='screen_resolution')),
                ('ip_certification', models.CharField(max_length=10, verbose_name='ip_certification')),
                ('internal_storage', models.CharField(max_length=10, verbose_name='internal_storage')),
                ('external_storage', models.CharField(max_length=10, verbose_name='external_storage')),
                ('WLAN', models.CharField(max_length=10, verbose_name='WLAN')),
                ('bluetooth', models.CharField(max_length=30, verbose_name='bluetooth')),
                ('NFC', models.BooleanField(default=True)),
                ('USB', models.CharField(max_length=10, verbose_name='USB')),
                ('wireless_charging', models.CharField(max_length=30, verbose_name='wireless_charging')),
                ('fast_charging', models.CharField(max_length=30, verbose_name='fast_charging')),
                ('chipset', models.CharField(max_length=30, verbose_name='chipset')),
                ('control_system', models.CharField(max_length=30, verbose_name='control_system')),
                ('mobile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mobile')),
            ],
        ),
        migrations.CreateModel(
            name='MobilePrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cash_price', models.FloatField(verbose_name='price')),
                ('price_6_months', models.FloatField(verbose_name='price')),
                ('price_12_months', models.FloatField(verbose_name='price')),
                ('price_24_months', models.FloatField(verbose_name='price')),
                ('price_36_months', models.FloatField(verbose_name='price')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('mobile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mobile', verbose_name='Mobile')),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.package', verbose_name='Package')),
            ],
            options={
                'verbose_name': 'MobilePrice',
                'verbose_name_plural': 'MobilePrices',
            },
        ),
        migrations.CreateModel(
            name='MobileCameraSpecification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rear_cam_lenses', models.IntegerField(verbose_name='rear_camera_lenses')),
                ('rear_cam_megapixel', models.CharField(max_length=30, verbose_name='rear_camera_megapixel')),
                ('back_cam_aperture', models.CharField(max_length=30, verbose_name='rear_camera_megapixel')),
                ('rear_cam_video_resolution', models.CharField(max_length=30, verbose_name='rear_camera_video_resolution')),
                ('front_cam_lenses', models.IntegerField(verbose_name='front_camera_lenses')),
                ('front_cam_megapixel', models.CharField(max_length=30, verbose_name='front_camera_megapixel')),
                ('front_cam_aperture', models.CharField(max_length=30, verbose_name='front_camera_aperture')),
                ('front_cam_video_resolution', models.CharField(max_length=30, verbose_name='front_camera_video_resolution')),
                ('mobile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.mobile')),
            ],
        ),
        migrations.AddField(
            model_name='mobile',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.mobilebrand', verbose_name='Brand'),
        ),
        migrations.CreateModel(
            name='MobileVariation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=50, verbose_name='value')),
                ('variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.variation')),
            ],
            options={
                'unique_together': {('variation', 'value')},
            },
        ),
    ]