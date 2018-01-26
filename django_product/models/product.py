#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/24 下午3:02
"""

__all__ = ['Product']

from django_perm.db import models
from django_erp.common.models import DataModel
from django.utils.translation import ugettext_lazy as _


class Product(DataModel):
    """产品"""
    template = models.ForeignKey(
        'django_product.ProductTemplate',
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name=_('product template'),
        help_text=_('the template of the product')
    )

    attributes = models.JSONField(
        _('attributes'),
        null=False,
        blank=False,
        default={},
        form='dict',
        help_text=_('the json value of the attributes dict')
    )

    prices = models.JSONField(
        _('prices'),
        null=False,
        blank=False,
        default={},
        form='dict',
        help_text=_('the json value of the flow over price dict')
    )

    attributes_md5 = models.CharField(
        _('attributes md5'),
        null=False,
        blank=False,
        max_length=40,
        help_text=_('the value of attribute dict json md5,for unique require')
    )

    in_code = models.CharField(
        _('inner code'),
        null=True,
        blank=False,
        max_length=190,
        help_text=_('the inner code of product for private using')
    )

    out_code = models.CharField(
        _('outer code'),
        null=True,
        blank=False,
        max_length=190,
        help_text=_('the outer code of product for public using')
    )

    weight = models.DecimalField(
        _('weight'),
        null=False,
        blank=True,
        max_digits=24,
        decimal_places=12,
        default=0,
        help_text=_("product's weight,uom is kg")
    )

    volume = models.DecimalField(
        _('volume'),
        null=False,
        blank=True,
        max_digits=24,
        decimal_places=12,
        default=0,
        help_text=_("product's volume,uom is m3")
    )

    salable = models.BooleanField(
        _('sale status'),
        null=False,
        blank=True,
        default=False,
        help_text=_('True means product can be sale')
    )

    purchasable = models.BooleanField(
        _('purchase status'),
        null=False,
        blank=True,
        default=False,
        help_text=_('True means product can be purchased')
    )

    rentable = models.BooleanField(
        _('rent status'),
        null=False,
        blank=True,
        default=False,
        help_text=_('True means product can be rented')
    )

    @property
    def uom(self):
        return self.template.uom

    def __str__(self):
        return '{}({})'.format(self.template.name, self.attributes_str)

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        unique_together = ('template', 'attributes_md5')

    @property
    def attributes_str(self):
        return '/'.join(
            [
                '{}:{}'.format(key, value)
                for key, value in self.attributes.items()
            ]
        )
