#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午10:04
"""

__all__ = ['Region']

from django_perm import models
from django.db.models import Manager
from django.utils.translation import ugettext_lazy as _


class Region(models.Model):
    """region"""

    class KeyManager(Manager):
        def get_by_natural_key(self, country, province, city, name):
            return self.get(
                city__province__country=country,
                city__province__name=province,
                city__name=city,
                name=name
            )

    city = models.ForeignKey(
        'django_base.City',
        null=False,
        blank=False,
        verbose_name=_('city'),
        help_text=_("the city of the region")
    )

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=90,
        help_text=_("the name of region")
    )

    class Meta:
        verbose_name = _('region')
        verbose_name_plural = _('region')
        unique_together = ('city', 'name')

    def __str__(self):
        return '{}/{}'.format(self.city, self.name)

    def natural_key(self):
        return self.city.natural_key() + (self.name,)

    natural_key.dependencies = ['django_base.City']
