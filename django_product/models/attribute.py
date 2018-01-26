#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/23 下午11:44
"""

__all__ = ['Attribute']

from django_perm.db import models
from django_erp.common.models import HistoryModel, SequenceModel
from django.utils.translation import ugettext_lazy as _


class Attribute(HistoryModel,SequenceModel):
    """属性"""
    name = models.CharField(
        _('attribute name'),
        null=False,
        blank=False,
        unique=True,
        max_length=190,
        help_text=_('the name of product attribute')
    )

    value = models.JSONField(
        _('value'),
        null=False,
        blank=False,
        form='list',
        help_text=_('json list of value for attribute')
    )

    class Meta:
        verbose_name = _('attribute')
        verbose_name_plural = _('attributes')

    def __str__(self):
        return self.name
