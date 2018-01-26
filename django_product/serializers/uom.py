#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/24 下午4:00
"""

__all__ = ['UOMSerializer']

from .. import models
from django_erp.rest.serializers import DataModelSerializer

class UOMSerializer(DataModelSerializer):
    class Meta:
        model = models.UOM
        fields = '__all__'