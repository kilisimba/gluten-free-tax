# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('achat', '0003_auto_20150326_2234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='achat',
            name='association',
        ),
    ]
