# Generated by Django 2.1.9 on 2019-06-19 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='myuser',
            name='address',
            field=models.CharField(blank=True, default='', max_length=200, null=True, verbose_name='地址'),
        ),
    ]
