#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午11:05
"""

__all__ = ['EmailAccountViewSet']

from .. import models
from .. import serializers
from django_erp.rest.viewsets import PermMethodViewSet

class EmailAccountViewSet(PermMethodViewSet):
    model = models.EmailAccount
    allow_actions = ('create', 'list', 'retrieve', 'update')
    serializer_class = serializers.EmailAccountSerializer