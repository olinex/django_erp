#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class SaleConfig(AppConfig):
    name = 'apps.sale'
    verbose_name = _('sale')
