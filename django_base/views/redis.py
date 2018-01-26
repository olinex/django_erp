#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/22 下午7:09
"""

__all__ = ['RedisViewSet']

from django_erp.common import Redis
from django.conf import settings
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from ..models import Message

class RedisViewSet(ViewSet):
    """
    get the redis data
    """

    def list(self,request):
        """return all of the redis data"""
        redis = Redis()
        value = [
            *redis.keys('argument_*')
        ]

        hash = [
            settings.SOCKET_ONLINE_GROUP_NAME,
        ]

        member = [
            *redis.keys('message_user_*')
        ]

        data = {
            'value': dict(zip(value,redis.mget(keys=value))) if value else {},
            'hash': {
                key: {k.decode('utf8'):v.decode('utf8') for k,v in redis.hgetall(key).items()}
                for key in hash
            },
            'member': {
                key.decode('utf-8'): redis.smembers(key)
                for key in member
            }
        }
        return Response(data)
