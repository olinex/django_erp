#!/usr/bin/env python3
#-*- coding:utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class ProductConfig(AppConfig):
    name = 'apps.product'
    verbose_name = _('product')

    def ready(self):
        from . import signals
