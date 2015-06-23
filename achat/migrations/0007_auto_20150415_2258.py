# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('achat', '0006_achat_taxable'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='achat',
            options={'ordering': ['-date', '-pk']},
        ),
    ]
