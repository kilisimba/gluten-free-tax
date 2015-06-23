# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbref', '0002_auto_20150114_2148'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='association',
            options={'verbose_name': 'Lookup Table'},
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterField(
            model_name='association',
            name='equivalent',
            field=models.ForeignKey(related_name='non-GF', verbose_name=b'non-gluten free', blank=True, to='dbref.Product', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='association',
            name='gluten_free',
            field=models.ForeignKey(related_name='GF', to='dbref.Product'),
            preserve_default=True,
        ),
    ]
