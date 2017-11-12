#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午8:18
"""

__all__ = ['ProvinceViewSet']

from .. import models
from .. import serializers
from .. import filters
from django_erp.rest.viewsets import DataViewSet


class ProvinceViewSet(DataViewSet):
    model = models.Province
    serializer_class = serializers.ProvinceSerializer
    filter_class = filters.ProvinceFilter