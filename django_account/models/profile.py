#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 上午11:39
"""

__all__ = ['Profile']

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from django_perm import models
from common.fields import ActiveLimitForeignKey, ActiveLimitOneToOneField

User = get_user_model()


class Profile(models.Model):
    """用户的其他信息"""
    SEX_CHOICES = (
        ('unknown', _('unknown')),
        ('male', _('male')),
        ('female', _('female')),
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
        'django_base.Address',
        null=True,
        blank=True,
        verbose_name=_("address"),
        related_name='locale_profiles',
        help_text=_("use's locale address")
    )

    default_send_address = ActiveLimitForeignKey(
        'django_base.Address',
        null=True,
        blank=True,
        verbose_name=_('default send address'),
        related_name='default_profiles',
        help_text=_("the default address which user wanted to reach the product")
    )

    usual_send_addresses = models.ManyToManyField(
        'django_base.Address',
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
