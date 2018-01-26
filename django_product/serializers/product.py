#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/24 下午4:43
"""

__all__ = ['ProductSerializer']

from .. import models
from django_erp.rest.serializers import DataModelSerializer

class ProductSerializer(DataModelSerializer):

    class Meta:
        model = models.Product
        fields = '__all__'