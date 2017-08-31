#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@author:    olinex
@time:      2017/8/24 下午2:30
'''

import os
import json
from hashlib import md5
from django.core.serializers.json import DjangoJSONEncoder

import os

PREFIX = 'DJANGO_ERP'

def setdefault(key,value):
    os.environ.setdefault(
        '{}_{}'.format(PREFIX,key),
        value
    )

def get_environ(key,):
    return os.environ.get('{}_{}'.format(PREFIX,key))


def md5_hexdigest(object):
    m = md5()
    m.update(json.dumps(object, cls=DjangoJSONEncoder).encode(('utf8')))
    return m.hexdigest()
