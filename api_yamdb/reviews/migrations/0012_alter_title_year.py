# Generated by Django 3.2.16 on 2023-05-14 14:58

import api.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0011_alter_title_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.SmallIntegerField(validators=[api.validators.validet_year], verbose_name='Год выпуска'),
        ),
    ]
