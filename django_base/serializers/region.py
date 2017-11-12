#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午3:34
"""

__all__ = ['RegionSerializer']

from .. import models
from django_erp.rest.serializers import DataModelSerializer


class RegionSerializer(DataModelSerializer):
    class Meta:
        model = models.Region
        fields = '__all__'