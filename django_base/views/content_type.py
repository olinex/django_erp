#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午10:41
"""

__all__ = ['ContentTypeViewSet']

from .. import filters
from django_erp.rest.viewsets import PermMethodViewSet
from django_erp.rest.serializers import ContentTypeSerializer
from django.contrib.contenttypes.models import ContentType

class ContentTypeViewSet(PermMethodViewSet):
    model = ContentType
    allow_actions = ('list', 'retrieve')
    serializer_class = ContentTypeSerializer
    filter_class = filters.ContentTypeFilter