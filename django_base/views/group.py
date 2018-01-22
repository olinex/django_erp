#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午11:01
"""

__all__ = ['GroupViewSet']

from .. import filters
from django.contrib.auth.models import Group
from django_erp.rest.viewsets import PermMethodViewSet
from django_erp.rest.serializers import GroupSerializer

class GroupViewSet(PermMethodViewSet):
    model = Group
    serializer_class = GroupSerializer
    filter_class = filters.GroupFilter