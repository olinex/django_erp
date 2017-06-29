# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-28 12:43
from __future__ import unicode_literals

from django.db import migrations
import djangoperm.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_auto_20170627_2226'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProcurementFromLocationSettings',
            new_name='ProcurementFromLocationSetting',
        ),
        migrations.AddField(
            model_name='route',
            name='map_md5',
            field=djangoperm.db.fields.CharField(default=1, help_text='路径顺序列表的的md5值', max_length=40, perms={'read': False, 'write': False}, unique=True, verbose_name='路径顺序列表的md5值'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='route',
            name='map',
            field=djangoperm.db.fields.JSONField(help_text='以json格式保存的路径顺序', json_type='list', perms={'read': False, 'write': False}),
        ),
        migrations.AlterField(
            model_name='route',
            name='name',
            field=djangoperm.db.fields.CharField(help_text='路线的名称', max_length=190, perms={'read': False, 'write': False}, unique=True, verbose_name='名称'),
        ),
    ]
