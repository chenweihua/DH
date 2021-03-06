# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-14 21:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('choose_stock', '0005_kmeansdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashFlowData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_name', models.CharField(max_length=16)),
                ('stock_id', models.CharField(max_length=8)),
                ('stock_date', models.DateField()),
                ('price_close', models.CharField(max_length=8)),
                ('var_degree', models.CharField(max_length=8)),
                ('maincash_in', models.CharField(max_length=8)),
                ('maincash_in_rate', models.CharField(max_length=8)),
                ('join_degree', models.CharField(max_length=8)),
                ('control_type', models.CharField(max_length=8)),
                ('main_cost', models.CharField(max_length=8)),
                ('stock_id_date', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='kmeansdata',
            name='price_open',
            field=models.CharField(max_length=8),
        ),
    ]
