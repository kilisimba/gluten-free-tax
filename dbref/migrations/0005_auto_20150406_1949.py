# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbref', '0004_auto_20150405_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='note',
            field=models.ForeignKey(blank=True, to='dbref.Note', null=True),
            preserve_default=True,
        ),
    ]
