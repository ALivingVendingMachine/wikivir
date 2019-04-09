# Generated by Django 2.2 on 2019-04-04 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topicTitle', models.CharField(max_length=256)),
                ('topicBody', models.CharField(max_length=2560)),
            ],
        ),
        migrations.AlterField(
            model_name='malwaresample',
            name='file',
            field=models.FileField(upload_to='samples/'),
        ),
    ]
