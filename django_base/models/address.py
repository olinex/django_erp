#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午10:05
"""

__all__ = ['Address']

from django_perm import models
from django.utils.translation import ugettext_lazy as _
from common.abstractModel import BaseModel


class Address(BaseModel):
    """the real address"""
    region = models.ForeignKey(
        'django_base.Region',
        null=False,
        blank=False,
        verbose_name=_('region'),
        help_text=_("the region of the address")
    )

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=190,
        help_text=_("the name of the address")
    )

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
        unique_together = ('region', 'name')

    def __str__(self):
        return '{}/{}'.format(self.region, self.name)
