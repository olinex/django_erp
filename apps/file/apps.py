#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FileConfig(AppConfig):
    name = 'apps.file'
    verbose_name = _('static file')
