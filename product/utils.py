#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from djangoperm.db import models

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