#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from djangoperm.db import models
from django.conf import settings


class QuantityField(models.DecimalField):
    '''数量单位'''

    def __init__(self, *args, uom, **kwargs):
        self.uom = uom
        kwargs['max_digits'] = kwargs.get('max_digits') or 24
        kwargs['decimal_places'] = kwargs.get('decimal_places') or 12
        super(QuantityField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(QuantityField, self).deconstruct()
        kwargs['uom'] = self.uom
        return name, path, args, kwargs


class ActiveLimitForeignKey(models.ForeignKey):
    '''可用外键约束'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_delete': False, 'is_active': True})
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        super(ActiveLimitForeignKey, self).__init__(*args, **kwargs)


class ActiveLimitOneToOneField(models.OneToOneField):
    '''可用外键约束'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_delete': False, 'is_active': True})
        super(ActiveLimitOneToOneField, self).__init__(*args, **kwargs)


class ActiveLimitManyToManyField(models.ManyToManyField):
    '''可用外键约束'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'is_delete': False, 'is_active': True})
        super(ActiveLimitManyToManyField, self).__init__(*args, **kwargs)


class PartnerForeignKey(models.ForeignKey):
    '''合作伙伴外键'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get('limit_choices_to', {'profile__is_partner': True, 'is_active': True})
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['to'] = settings.AUTH_USER_MODEL
        super(PartnerForeignKey, self).__init__(*args, **kwargs)


class LocationForeignKey(models.ForeignKey):
    '''库位外键'''

    def __init__(self, *args, **kwargs):
        kwargs['limit_choices_to'] = kwargs.get(
            'limit_choices_to',
            {'is_delete': False, 'is_active': True, 'is_virtual': False}
        )
        kwargs['on_delete'] = kwargs.get('on_delete', models.PROTECT)
        kwargs['to'] = 'stock.Location'
        super(PartnerForeignKey, self).__init__(*args, **kwargs)


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
