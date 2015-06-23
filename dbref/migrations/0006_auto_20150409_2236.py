# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbref', '0005_auto_20150406_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='association',
            name='equivalent',
            field=models.ForeignKey(related_name='nonGF', verbose_name=b'non-gluten free', blank=True, to='dbref.Product', null=True),
        ),
    ]
