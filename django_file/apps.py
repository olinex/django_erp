#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoFileConfig(AppConfig):
    name = 'django_file'
    verbose_name = _('static file')
