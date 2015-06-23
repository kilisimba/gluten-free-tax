# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbref', '0003_auto_20150322_2204'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('note', models.TextField(max_length=800)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='company',
            name='certification',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='company',
            name='name',
            field=models.CharField(default=b'Unknown', max_length=200),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='note',
            field=models.ForeignKey(blank=True, to='dbref.Note', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='note',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='company',
            name='validation_date',
            field=models.CharField(max_length=100, null=True, blank=True),
            preserve_default=True,
        ),
    ]
