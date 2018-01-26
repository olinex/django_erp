#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/24 下午4:38
"""

__all__ = ['ProductTemplateSerializer']

from .. import models
from django_erp.rest.serializers import DataModelSerializer

class ProductTemplateSerializer(DataModelSerializer):

    class Meta:
        model = models.ProductTemplate
        fields = '__all__'