#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/24 下午3:34
"""

__all__ = ['ProductTemplate']

from django_perm.db import models
from django_erp.common.models import DataModel
from django.utils.translation import ugettext_lazy as _


class ProductTemplate(DataModel):
    """product template"""
    STOCK_TYPE = (
        ('service', _('service')),
        ('digital', _('digital')),
        ('stock-expiration', _('stock expiration')),
        ('stock-no-expiration', _('stock not expiration')),
        ('consumable', _('consumable product'))
    )
    name = models.CharField(
        _('name'),
        unique=True,
        null=False,
        blank=False,
        max_length=190,
        help_text=_("product template's name")
    )

    stock_type = models.CharField(
        _('stock type'),
        null=False,
        blank=False,
        max_length=20,
        choices=STOCK_TYPE,
        help_text=_('the type of product how to stock')
    )

    attributes = models.ManyToManyField(
        'django_product.Attribute',
        verbose_name=_('attributes'),
        help_text=_('the attributes and product relationship')
    )

    uom = models.ForeignKey(
        'django_product.UOM',
        null=False,
        blank=False,
        editable=False,
        verbose_name=_('uom'),
        on_delete=models.PROTECT,
        help_text=_("product's unit of measurement")
    )

    sequence = models.PositiveIntegerField(
        _('sequence'),
        null=False,
        blank=True,
        default=0,
        help_text=_('the order of product template')
    )

    detail = models.CharField(
        _('detail'),
        null=False,
        blank=True,
        default='',
        max_length=190,
        help_text=_('the detail message of product template')
    )

    in_description = models.TextField(
        _('inner description'),
        null=False,
        blank=True,
        default='',
        help_text=_('the description of product template for private using')
    )

    out_description = models.TextField(
        _('outer description'),
        null=False,
        blank=True,
        default='',
        help_text=_('the description of product template for public using')
    )

    category = models.ForeignKey(
        'django_product.ProductCategory',
        null=True,
        blank=True,
        verbose_name=_('product category'),
        help_text=_('the category of product')
    )

    class Meta:
        verbose_name = _('product template')
        verbose_name_plural = _('product templates')

    def __str__(self):
        return self.name

    @property
    def attribute_combination(self):
        from itertools import product
        attributes = self.attributes.all().values_list('name', 'value', 'extra_price')
        key_list = [attr[0] for attr in attributes]
        attribute_value = [zip(*attr[1:]) for attr in attributes]
        for value_tuple in product(*attribute_value):
            yield dict(zip(key_list, value_tuple))