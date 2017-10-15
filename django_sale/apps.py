#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class DjangoSaleConfig(AppConfig):
    name = 'django_sale'
    verbose_name = _('sale')
