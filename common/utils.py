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


def md5_hexdigest(object):
    m = md5()
    m.update(json.dumps(object, cls=DjangoJSONEncoder).encode(('utf8')))
    return m.hexdigest()


def include(arg, namespace=None):
    from django.conf.urls import include as origin_include
    return origin_include(arg=arg, namespace=namespace, app_name=namespace)
