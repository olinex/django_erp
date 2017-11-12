#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午2:45
"""

__all__ = ['ProvinceSerializer']

from .. import models
from django_erp.rest.serializers import DataModelSerializer


class ProvinceSerializer(DataModelSerializer):
    class Meta:
        model = models.Province
        fields = '__all__'


