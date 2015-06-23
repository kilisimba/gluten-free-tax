# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbref', '0006_auto_20150409_2236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='association',
            options={'ordering': ['gluten_free__description', 'equivalent__description'], 'verbose_name': 'Lookup Table'},
        ),
    ]
