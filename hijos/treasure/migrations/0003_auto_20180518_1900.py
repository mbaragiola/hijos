# Generated by Django 2.0.4 on 2018-05-18 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0002_auto_20180424_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='begin',
            field=models.DateField(help_text='YYYY-MM-DD', verbose_name='begin'),
        ),
        migrations.AlterField(
            model_name='period',
            name='end',
            field=models.DateField(help_text='YYYY-MM-DD', verbose_name='end'),
        ),
    ]