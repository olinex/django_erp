#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/24 下午3:48
"""

__all__ = ['ProductCategorySerializer']

from .. import models
from django_erp.rest.serializers import DataModelSerializer

class ProductCategorySerializer(DataModelSerializer):
    class Meta:
        model = models.ProductCategory
        fields = '__all__'