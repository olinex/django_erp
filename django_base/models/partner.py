#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 上午11:41
"""

__all__ = [
    'Partner',
]

from django_perm.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django_erp.common.models import BaseModel

User = get_user_model()


class Partner(BaseModel):
    """partner"""
    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=90,
        help_text=_("partner's name"),
    )

    phone = models.CharField(
        _('phone'),
        null=False,
        blank=False,
        default='',
        max_length=32,
        help_text=_('the phone of the partner')
    )

    region = models.ForeignKey(
        'Region',
        null=False,
        blank=False,
        help_text=_("partner's region")
    )

    address = models.CharField(
        _('address'),
        null=False,
        blank=False,
        max_length=190,
        help_text=_("partner's address detail")
    )

    is_company = models.BooleanField(
        _('is company'),
        default=False,
        help_text=_('the status of partner is a company')
    )

    sale_able = models.BooleanField(
        _('sale status'),
        default=True,
        help_text=_('the status of partner whether can buy product')
    )

    purchase_able = models.BooleanField(
        _('purchase status'),
        default=False,
        help_text=_('the status of partner whether can purchase product')
    )

    class Meta:
        verbose_name = _('partner')
        verbose_name_plural = _('partners')
        unique_together = ('region', 'address')

    def __str__(self):
        return self.name
