#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午10:30
"""

__all__ = ['ArgumentViewSet']

from .. import models, serializers, filters
from .mixin import MessageModelMixin
from django_erp.rest.viewsets import PermMethodViewSet


class ArgumentViewSet(MessageModelMixin,PermMethodViewSet):
    model = models.Argument
    allow_actions = ('list', 'retrieve', 'update')
    serializer_class = serializers.ArgumentSerializer
    filter_class = filters.ArgumentFilter
