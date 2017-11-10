#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 上午11:41
"""

__all__ = [
    'Partner',
]

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from django_perm import models
from common.abstractModel import BaseModel, TreeModel
from common.fields import ActiveLimitForeignKey, ActiveLimitOneToOneField

User = get_user_model()


class Partner(BaseModel, TreeModel):
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

    address = ActiveLimitOneToOneField(
        'django_base.Address',
        null=True,
        blank=True,
        verbose_name=_('partner address'),
        related_name='locale_partners',
        help_text=_('the location address of the partner')
    )

    default_send_address = ActiveLimitForeignKey(
        'django_base.Address',
        null=True,
        blank=True,
        verbose_name=_('default send address'),
        related_name='default_partners',
        help_text=_('the default address for partner to receive product')
    )

    usual_send_addresses = models.ManyToManyField(
        'django_base.Address',
        verbose_name=_('usual send addresses'),
        related_name='usual_partners',
        help_text=_("addresses that will be usually use by user")
    )

    managers = models.ManyToManyField(
        User,
        verbose_name=_('managers'),
        help_text=_('users who are manager of this partner')
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
        unique_together = ('name', 'address')

    def __str__(self):
        return self.name
