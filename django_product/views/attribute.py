#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午10:30
"""

__all__ = ['AttributeViewSet']

from .. import models, serializers, filters
from django_erp.rest.viewsets import PermMethodViewSet


class AttributeViewSet(PermMethodViewSet):
    model = models.Attribute
    serializer_class = serializers.AttributeSerializer
    filter_class = filters.AttributeFilter

