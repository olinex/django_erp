#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from djangoperm.db import models
from django.conf import settings


class LocationForeignKey(models.ForeignKey):
    '''库位外键'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get(
            'limit_choices_to',
            {'is_delete': False, 'is_active': True, 'is_virtual': False}
        )
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['to'] = 'stock.Location'
        super(LocationForeignKey, self).__init__(*args, **kwargs)


def floor_value(instance, field_name):
    '''
    获取实例指定字段通过单位转换精度的值
    :param instance: 数据表实例
    :param field: 字段名
    :return: decimal
    '''
    uom_name = instance.model._meta.fields[field_name].uom
    uom = getattr(instance, uom_name)
    return uom.floor_value(getattr(instance, field_name))


def uom_format_value(instance, field, uom_name):
    '''
    获取实例指定字段进行单位转换后的值
    :param instance: 数据表实例
    :param field: 字段名
    :param uom: 单位
    :return: decimal
    '''
    return instance.get(field)
