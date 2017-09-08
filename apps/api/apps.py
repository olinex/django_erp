#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ApiConfig(AppConfig):
    name = 'apps.api'
    verbose_name = _('api')

    def ready(self):
        from . import signals

