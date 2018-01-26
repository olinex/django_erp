#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/24 下午2:55
"""

__all__ = ['Lot']

from django_perm.db import models
from django_erp.common.models import DataModel
from django.utils.translation import ugettext_lazy as _


class Lot(DataModel):
    """lot number"""
    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        unique=True,
        max_length=90,
        help_text=_('the name of lot')
    )

    product = models.ForeignKey(
        'django_product.Product',
        null=False,
        blank=False,
        verbose_name=_('product'),
        help_text=_('the product of the lot')
    )

    class Meta:
        verbose_name = _('lot')
        verbose_name_plural = _('lots')

    def __str__(self):
        return self.name
