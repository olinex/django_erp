#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django_perm import models
from django.db.models import Manager
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from common.abstractModel import BaseModel

User = get_user_model()


class Province(models.Model):
    '''province'''

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
        return '{}/{}'.format(self.get_country_display(),self.name)

    def natural_key(self):
        return (self.country, self.name)


class City(models.Model):
    '''city'''

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


class Region(models.Model):
    '''region'''

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
        return '{}/{}'.format(self.city,self.name)

    def natural_key(self):
        return self.city.natural_key() + (self.name,)

    natural_key.dependencies = ['django_base.City']


class Address(BaseModel):
    '''the real address'''
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
        return '{}/{}'.format(self.region,self.name)
