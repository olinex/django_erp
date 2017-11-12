#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/11 上午10:50
"""

__all__ = ['Address']

from django_perm import models
from django.utils.translation import ugettext_lazy as _


class Address(models.Model):
    """address"""

    region = models.ForeignKey(
        'Region',
        null=False,
        blank=False,
        verbose_name=_('region'),
        help_text=_("the region of the address")
    )

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=90,
        help_text=_("the name of address")
    )

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('address')

    def __str__(self):
        return '{}/{}'.format(self.region, self.name)