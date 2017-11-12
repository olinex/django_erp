#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoBaseConfig(AppConfig):
    name = 'django_base'
    verbose_name = _('base')

    def ready(self):
        from . import signals
