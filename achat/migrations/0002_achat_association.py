# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbref', '0002_auto_20150114_2148'),
        ('achat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='achat',
            name='association',
            field=models.ForeignKey(blank=True, to='dbref.Association', null=True),
            preserve_default=True,
        ),
    ]
