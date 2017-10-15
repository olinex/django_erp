#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoStockConfig(AppConfig):
    name = 'django_stock'
    verbose_name = _('stock config')

    def ready(self):
        from . import signals

