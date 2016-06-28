# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-27 20:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choose_stock', '0004_name_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='KmeansData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_name', models.CharField(max_length=16)),
                ('stock_id', models.CharField(max_length=8)),
                ('stock_date', models.DateField()),
                ('price_open', models.CharField(max_length=10)),
                ('price_high', models.CharField(max_length=8)),
                ('price_low', models.CharField(max_length=8)),
                ('price_close', models.CharField(max_length=8)),
                ('stock_volumn', models.CharField(max_length=20)),
                ('stock_id_date', models.CharField(max_length=20, unique=True)),
            ],
        ),
    ]