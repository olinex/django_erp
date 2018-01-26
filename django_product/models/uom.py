#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/23 下午2:39
"""

__all__ = ['UOM']

from django.db.models import Manager
from django_perm.db import models
from django_erp.common.models import DataModel
from django.utils.translation import ugettext_lazy as _


class UOM(DataModel):
    """计量单位"""

    class KeyManager(Manager):
        def get_by_natural_key(self, symbol):
            return self.get(symbol=symbol)

    objects = KeyManager()

    UOM_CATEGORY = (
        ('m', _('meter')),
        ('kg', _('kilogram')),
        ('s', _('second')),
        ('A', _('Ampere')),
        ('K', _('Kelvins')),
        ('J', _('Joule')),
        ('m2', _('square meter')),
        ('m3', _('cubic meter')),
        ('unit', _('unit')),
        ('yuan', _('yuan'))
    )

    ROUND_METHOD = (
        ('ROUND_CEILING', _('round ceiling')),  # 趋向无穷取整
        ('ROUND_DOWN', _('round down')),  # 趋向0取整
        ('ROUND_FLOOR', _('round floor')),  # 趋向负无穷取整
        ('ROUND_HALF_DOWN', _('round half down')),  # 末位大于五反向零取整,否则趋向零取整
        ('ROUND_HALF_EVEN', _('round half even')),  # 末位大于五反向零取整,小于五趋向零取整,遇五前位为奇数反向零取整
        ('ROUND_HALF_UP', _('round half up')),  # 末位大于等于五反向零取整,否则趋向零取整
        ('ROUND_UP', _('round up')),  # 反向0取整
        ('ROUND_05UP', _('round zero and half up'))  # 取整位数为零或五时反向零取整,否则趋向零取整
    )

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=20,
        unique=True,
        help_text=_("the verbose of the uom")
    )

    symbol = models.CharField(
        _('symbol'),
        null=False,
        blank=False,
        unique=True,
        max_length=10,
        help_text=_("the symbol of the uom in math")
    )

    decimal_places = models.PositiveSmallIntegerField(
        _('decimal places'),
        null=False,
        blank=False,
        default=3,
        help_text=_('the decimal places of the uom value')
    )

    round_method = models.CharField(
        _('round method'),
        null=False,
        blank=False,
        max_length=20,
        choices=ROUND_METHOD,
        default='ROUND_CEILING',
        help_text=_("the method will be used when the value of uom was rounding")
    )

    ratio = models.DecimalField(
        _('ratio'),
        max_digits=24,
        decimal_places=12,
        null=False,
        blank=False,
        help_text=_("""
        the ratio of the uom compare with standard unit,when ratio is bigger than 1,
        means uom is greater than standard unit
        """)
    )

    category = models.CharField(
        _('category'),
        null=False,
        blank=False,
        max_length=10,
        choices=UOM_CATEGORY,
        help_text=_("""
        the category of the uom,uom value can be converted to other uom value only when their in the same category
        """)
    )

    @property
    def ratio_type(self):
        if self.ratio > 1:
            return _('bigger')
        if self.ratio == 1:
            return _('equal')
        if 0 < self.ratio < 1:
            return _('smaller')

    class Meta:
        verbose_name = _('uom')
        verbose_name_plural = _('uoms')

    def __str__(self):
        return '{}({})'.format(self.name, self.symbol)

    def natural_key(self):
        return (self.symbol,)

    def accuracy_convert(self, value):
        """
        convert value's precision to this uom's precision
        :param value: decimal
        :return: decimal
        """
        import decimal
        with decimal.localcontext() as ctx:
            ctx.prec = 24
            return value.quantize(
                decimal.Decimal('0.' + ('0' * self.decimal_places)),
                rounding=getattr(decimal, self.round_method),
            )

    def convert(self, value, to_uom):
        """
        convert value as this uom precision and ratio to another uom
        :param value: decimal
        :param to_uom: uom
        :return: decimal
        """
        if self.category == to_uom.category:
            new_value = value * self.ratio / to_uom.ratio
            return to_uom.accuracy_convert(new_value)
        raise AttributeError(_('uom can not be convert to other uom until their category is the same'))
