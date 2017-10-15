#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoAccountConfig(AppConfig):
    name = 'django_account'
    verbose_name = _('account')

    def ready(self):
        from . import signals
