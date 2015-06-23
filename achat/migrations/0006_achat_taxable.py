# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('achat', '0005_achat_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='achat',
            name='taxable',
            field=models.BooleanField(default=False),
        ),
    ]
