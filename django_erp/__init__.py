#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import json
from .celery import app as celery_app

__all__ = ('celery_app','setdefault','get_environ')

PREFIX = 'DJANGO_ERP'

def setdefault(key,value):
    os.environ.setdefault(
        '{}_{}'.format(PREFIX,key),
        json.dumps(value)
    )

def get_environ(key):
    return json.loads(os.environ.get('{}_{}'.format(PREFIX,key)))

