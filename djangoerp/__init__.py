#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import pymysql
from . import privates
from .celery import app as celery_app

__all__ = ['celery_app']

pymysql.install_as_MySQLdb()

