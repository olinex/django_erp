#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from apps.djangoperm import models


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

def get_quantity_by_uom(instance,field_name,uom=None):
    '''获得对象指定单位格式的数量'''
    from functools import reduce
    quantity = getattr(instance,field_name)
    default_uom = reduce(getattr,[instance] + instance.__class__._meta.fields[field_name].uom.join('.'))
    if uom:
        return default_uom.convert(quantity,to_uom=uom)
    return default_uom.accuracy_convert(quantity)

