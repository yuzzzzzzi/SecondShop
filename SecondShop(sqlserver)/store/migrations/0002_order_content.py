# Generated by Django 2.1.9 on 2019-06-14 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='content',
            field=models.CharField(default=1, max_length=400, verbose_name='商品'),
            preserve_default=False,
        ),
    ]