#!/usr/bin/env python3
# -*- coding:utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class DjangoProductConfig(AppConfig):
    name = 'django_product'
    verbose_name = _('product')

    def ready(self):
        from . import signals
