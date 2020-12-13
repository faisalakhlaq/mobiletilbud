# Generated by Django 3.1.3 on 2020-12-12 01:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mobiles', '0018_mobilebrand_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='mobile',
            name='launch_date',
            field=models.DateField(blank=True, null=True, verbose_name='Launch Date'),
        ),
        migrations.AlterField(
            model_name='mobile',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mobiltelefoner', to='mobiles.mobilebrand', verbose_name='Brand'),
        ),
    ]