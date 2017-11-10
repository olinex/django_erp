#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午10:02
"""

__all__ = ['City']

from django_perm import models
from django.db.models import Manager
from django.utils.translation import ugettext_lazy as _


class City(models.Model):
    """city"""

    class KeyManager(Manager):
        def get_by_natural_key(self, country, province, name):
            return self.get(
                province__country=country,
                province__name=province,
                name=name
            )

    objects = KeyManager()

    province = models.ForeignKey(
        'django_base.Province',
        null=False,
        blank=False,
        verbose_name=_('province'),
        help_text=_("the province of the city")
    )

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=90,
        help_text=_("the name of city")
    )

    class Meta:
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        unique_together = ('province', 'name')

    def __str__(self):
        return str(self.province) + '/' + self.name

    def natural_key(self):
        return self.province.natural_key() + (self.name,)

    natural_key.dependencies = ['django_base.Province']
