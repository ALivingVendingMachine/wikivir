# Generated by Django 2.2 on 2019-04-11 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20190410_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='malwaresample',
            name='objdump',
            field=models.CharField(max_length=256000),
        ),
        migrations.AlterField(
            model_name='malwaresample',
            name='readelf',
            field=models.CharField(max_length=256000),
        ),
    ]
