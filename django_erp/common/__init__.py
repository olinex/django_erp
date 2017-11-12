#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import redis
from django.conf import settings
from decimal import Decimal as D

__all__ = ["Redis"]


class Redis(redis.Redis):
    """
    A class that store connection pool and always return the same pool connection
    """
    _REDIS_POOL = redis.ConnectionPool(**settings.REDIS_CONF)

    def __init__(self, connection_pool=_REDIS_POOL, *args, **kwargs):
        super(Redis, self).__init__(
            connection_pool=connection_pool,
            *args,
            **kwargs
        )

    def hmget_sum(self, name, *fields):
        """
        get the sum of hash'sfields
        :param name: string
        :param fields: tuple
        :return: decimal
        """
        return sum(map(lambda num: D(num.decode) if num is not None else 0, self.hmget(
            name=name,
            keys=fields
        )))

    def zscore_sum(self, name, *scores):
        """
        get the sum of scores of the name
        :param name: string
        :param scores: tuple
        :return: decimal
        """
        return sum(map(
            lambda num: D(num) if num is not None else 0,
            [self.zscore(name, score) for score in scores]
        ))
