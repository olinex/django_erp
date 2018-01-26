#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/16 下午8:36
"""

__all__ = ['EmailAccount']

from django_perm.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django_erp.common.validators import IPPortValidator
from django.core.mail import get_connection

User = get_user_model()


class EmailAccount(models.Model):
    user = models.OneToOneField(
        User,
        null=False,
        blank=False,
        primary_key=True,
        verbose_name=_('email_account'),
        help_text=_("email's owner")
    )

    host = models.URLField(
        _('email host'),
        null=False,
        blank=False,
        max_length=64,
        help_text=_("the host of the email")
    )

    port = models.PositiveSmallIntegerField(
        _('email port'),
        null=False,
        blank=False,
        validators=[IPPortValidator]
    )

    username = models.CharField(
        _('email user name'),
        null=False,
        blank=False,
        max_length=128,
        help_text=_("the user name of the email")
    )

    password = models.CharField(
        _('email user password'),
        null=False,
        blank=False,
        max_length=128,
        help_text=_("the user password of the email")
    )

    class Meta:
        verbose_name = _('email account')
        verbose_name_plural = _('email accounts')

    @property
    def connection(self):
        return get_connection(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )