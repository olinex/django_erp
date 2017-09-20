#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.conf import settings
from django.db.models import Manager
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from django_perm import models
from common.abstractModel import BaseModel, TreeModel
from common.fields import ActiveLimitForeignKey, ActiveLimitOneToOneField, ActiveLimitManyToManyField

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
        'django_account.Province',
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

    natural_key.dependencies = ['django_account.Province']


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
        'django_account.City',
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

    natural_key.dependencies = ['django_account.City']


class Address(BaseModel):
    '''the real address'''
    region = models.ForeignKey(
        'django_account.Region',
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


class Profile(models.Model):
    '''用户的其他信息'''
    SEX_CHOICES = (
        ('unknown', _('unknown')),
        ('male',    _('male')),
        ('female',  _('female')),
    )

    user = models.OneToOneField(
        User,
        primary_key=True,
        verbose_name=_('user'),
        help_text=_('the unique user bind with profile')
    )

    sex = models.CharField(
        _('sex'),
        null=False,
        default='unknown',
        max_length=10,
        choices=SEX_CHOICES,
        help_text=_("the sex of the user")
    )

    phone = models.CharField(
        _('phone'),
        max_length=11,
        null=True,
        blank=False,
        unique=True,
        default=None,
        help_text=_("the user's phone number")
    )

    language = models.CharField(
        _('language'),
        null=True,
        blank=False,
        default='zh-han',
        max_length=20,
        choices=settings.LANGUAGES,
        help_text=_("user's mother language")
    )

    address = ActiveLimitOneToOneField(
        'django_account.Address',
        null=True,
        blank=True,
        verbose_name=_("address"),
        related_name='locale_profiles',
        help_text=_("use's locale address")
    )

    default_send_address = ActiveLimitForeignKey(
        'django_account.Address',
        null=True,
        blank=True,
        verbose_name=_('default send address'),
        related_name='default_profiles',
        help_text=_("the default address which user wanted to reach the product")
    )

    usual_send_addresses = ActiveLimitManyToManyField(
        'django_account.Address',
        blank=True,
        verbose_name=_('usual send address'),
        related_name='usual_profiles',
        help_text=_("addresses that will be usually use by user")
    )

    mail_notice = models.BooleanField(
        _('nail notice'),
        default=True,
        help_text=_("True means that user will receive mail on the web")
    )

    online_notice = models.BooleanField(
        _('online notice'),
        default=False,
        help_text=_("True means that user will tell others user's online status")
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return '{}-{}'.format(
            self.user.id,
            self.user.get_full_name() or self.user.get_username()
        )


class Partner(BaseModel, TreeModel):
    '''partner'''
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
        'django_account.Address',
        null=True,
        blank=True,
        verbose_name=_('partner address'),
        related_name='locale_partners',
        help_text=_('the location address of the partner')
    )

    default_send_address = ActiveLimitForeignKey(
        'django_account.Address',
        null=True,
        blank=True,
        verbose_name=_('default send address'),
        related_name='default_partners',
        help_text=_('the default address for partner to receive product')
    )

    usual_send_addresses = ActiveLimitManyToManyField(
        'django_account.Address',
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
