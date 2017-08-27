#!/usr/bin/env python3
# -*- coding:utf-8 -*-

'''
@author:    olinex
@time:      2017/8/24 下午2:30
'''

import json
from hashlib import md5
from django.core.serializers.json import DjangoJSONEncoder


def md5_hexdigest(object):
    m = md5()
    m.update(json.dumps(object, cls=DjangoJSONEncoder).encode(('utf8')))
    return m.hexdigest()
