#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
@author:    olinex
@time:      2017/8/31 下午9:19
'''

import random
import string
from . import setdefault

setdefault('SECRET_KEY', "".join(random.choice(string.printable) for i in range(255)))
setdefault('DEBUG', True)
setdefault('FILE_SERVICE', False)
setdefault('SETUP_TOOLS', True)
setdefault('PRIVATE_HOSTS',['107.191.60.188'])
setdefault('DATABASES',{
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_erp',
        'USER': 'django_erp',
        'PASSWORD': 'n7kUTkqcNsM8X53z',
        'HOST': 'localhost',
        'PORT': '5432',
    }
})
setdefault('CHANNEL_HOST','redis://:Q4oYDQ5mIsYO8GRz@localhost:6379/2')
setdefault('REDIS_CONF_HOST','localhost')
setdefault('REDIS_CONF_PORT','6379')
setdefault('REDIS_CONF_DB','1')
setdefault('REDIS_CONF_PASSWORD','Q4oYDQ5mIsYO8GRz')

setdefault('CELERY_BROKER_URL','redis://localhost:6379/3')
setdefault('CELERY_RESULT_BACKEND','redis://localhost:6379/4')

setdefault('DEFAULT_FROM_EMAIL','djangoerp@163.com')
setdefault('EMAIL_HOST','smtp.163.com')
setdefault('EMAIL_PORT','25')
setdefault('EMAIL_HOST_USER','djangoerp')
setdefault('EMAIL_HOST_PASSWORD','pehVp0NWvw357zKi')

setdefault('REDIS_CACHE_LOCATION','redis://127.0.0.1:6379/0')

