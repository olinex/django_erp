#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午3:31
"""

__all__ = ['CitySerializer']

from .. import models
from django_erp.rest.serializers import DataModelSerializer


class CitySerializer(DataModelSerializer):
    class Meta:
        model = models.City
        fields = '__all__'