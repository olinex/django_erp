#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午8:33
"""

__all__ = ['RegionViewSet']

from .. import models
from .. import serializers
from django_erp.rest.viewsets import DataViewSet


class RegionViewSet(DataViewSet):
    model = models.Region
    serializer_class = serializers.RegionSerializer