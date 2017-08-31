#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
import pymysql
from .celery import app as celery_app

__all__ = ('celery_app','setdefault','get_environ')

pymysql.install_as_MySQLdb()


PREFIX = 'DJANGO_ERP'

def setdefault(key,value):
    os.environ.setdefault(
        '{}_{}'.format(PREFIX,key),
        value
    )

def get_environ(key,):
    return os.environ.get('{}_{}'.format(PREFIX,key))

