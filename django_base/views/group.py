#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午11:01
"""

__all__ = ['GroupViewSet']

from .. import serializers, filters
from django.contrib.auth.models import Group
from django_erp.rest.viewsets import PermMethodViewSet

class GroupViewSet(PermMethodViewSet):
    model = Group
    serializer_class = serializers.GroupSerializer
    filter_class = filters.GroupFilter