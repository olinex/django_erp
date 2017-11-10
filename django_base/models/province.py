#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午10:01
"""

__all__ = ['Province']

from django_perm import models
from django.db.models import Manager
from django.utils.translation import ugettext_lazy as _


class Province(models.Model):
    """province"""

    COUNTRIES = (
        ('China', _('China')),
    )

    class KeyManager(Manager):
        def get_by_natural_key(self, country, name):
            return self.get(country=country, name=name)

    objects = KeyManager()

    country = models.CharField(
        _('country'),
        null=False,
        blank=False,
        choices=COUNTRIES,
        max_length=90,
        help_text=_("province's country")
    )

    name = models.CharField(
        _('name'),
        null=False,
        blank=False,
        max_length=90,
        help_text=_("the name of province")
    )

    class Meta:
        verbose_name = _('province')
        verbose_name_plural = _('provinces')
        unique_together = ('country', 'name')

    def __str__(self):
        return '{}/{}'.format(self.get_country_display(), self.name)

    def natural_key(self):
        return self.country, self.name
