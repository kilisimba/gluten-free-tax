# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Association',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField(max_length=800)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('validation_date', models.CharField(max_length=100)),
                ('note', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=200)),
                ('unit', models.DecimalField(default=0, max_digits=8, decimal_places=2)),
                ('price', models.DecimalField(default=0, max_digits=8, decimal_places=2)),
                ('gluten_free', models.BooleanField(default=False)),
                ('category', models.ForeignKey(blank=True, to='dbref.Category', null=True)),
                ('company', models.ForeignKey(blank=True, to='dbref.Company', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=200)),
                ('company', models.ForeignKey(to='dbref.Company')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='brand',
            name='company',
            field=models.ForeignKey(blank=True, to='dbref.Company', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='association',
            name='equivalent',
            field=models.ForeignKey(related_name='gluten', blank=True, to='dbref.Product', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='association',
            name='gluten_free',
            field=models.ForeignKey(related_name='gluten-free', to='dbref.Product'),
            preserve_default=True,
        ),
    ]
