#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULES','djangoerp.settings')

app = Celery('djangoerp')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()