# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('achat', '0004_remove_achat_association'),
    ]

    operations = [
        migrations.AddField(
            model_name='achat',
            name='quantity',
            field=models.SmallIntegerField(default=1),
        ),
    ]
