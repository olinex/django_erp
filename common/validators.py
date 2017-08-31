#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
@author:    olinex
@time:      2017/8/30 下午1:38
'''

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def NotZeroValidator(value):
    if value == 0:
        raise ValidationError(
            _('%(value)s can not equal to zero'),
            params={'value':value}
        )