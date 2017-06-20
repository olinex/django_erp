#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import redis
from django.conf import settings

__all__ = ['Redis']


class Redis(redis.Redis):
    '''
    A class that store connection pool and always return the same pool connection
    '''
    _REDIS_POOL = redis.ConnectionPool(**settings.REDIS_CONF)

    def __init__(self, connection_pool=_REDIS_POOL, *args, **kwargs):
        super(redis.Redis, self).__init__(
            connection_pool=connection_pool,
            *args,
            **kwargs
        )
