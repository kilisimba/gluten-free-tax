# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('achat', '0002_achat_association'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pending',
            fields=[
                ('achat', models.OneToOneField(primary_key=True, default=0, serialize=False, to='achat.Achat')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='achat',
            name='association',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='achat',
            name='brand',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='achat',
            name='description',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='achat',
            name='equivalent',
            field=models.CharField(max_length=200, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='achat',
            name='equivalent_price',
            field=models.DecimalField(default=0, verbose_name=b'price', max_digits=8, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='achat',
            name='equivalent_unit',
            field=models.DecimalField(default=0, verbose_name=b'unit', max_digits=8, decimal_places=2),
            preserve_default=True,
        ),
    ]
