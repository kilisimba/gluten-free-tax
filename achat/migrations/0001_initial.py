# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Achat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('description', models.CharField(max_length=200)),
                ('brand', models.CharField(max_length=200)),
                ('unit', models.DecimalField(default=0, max_digits=8, decimal_places=2)),
                ('price', models.DecimalField(default=0, max_digits=8, decimal_places=2)),
                ('equivalent', models.CharField(max_length=200)),
                ('equivalent_unit', models.DecimalField(default=0, max_digits=8, decimal_places=2)),
                ('equivalent_price', models.DecimalField(default=0, max_digits=8, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
