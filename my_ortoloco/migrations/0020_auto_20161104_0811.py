# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-11-04 07:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_ortoloco', '0019_auto_20161103_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='extraabo',
            name='canceled',
            field=models.BooleanField(default=False, verbose_name=b'gek\xc3\xbcndigt'),
        ),
        migrations.AlterField(
            model_name='extraabo',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='extra_abos', to='my_ortoloco.ExtraAboType'),
        ),
    ]
