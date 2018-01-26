#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/23 下午2:13
"""

__all__ = ['ProductCategory']

from django_perm.db import models
from django_erp.common.models import DataModel
from django.utils.translation import ugettext_lazy as _


class ProductCategory(DataModel):
    """product category"""
    name = models.CharField(
        _('name'),
        primary_key=True,
        max_length=90,
        help_text=_('the name of product category')
    )

    class Meta:
        verbose_name = _('product category')
        verbose_name_plural = _('product categories')

    def __str__(self):
        return self.name
