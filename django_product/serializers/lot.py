#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/24 下午4:14
"""

__all__ = ['LotSerializer']

from .. import models
from rest_framework import serializers
from django_erp.rest.fields import StatePrimaryKeyRelatedField
from django_erp.rest.serializers import DataModelSerializer


class LotSerializer(DataModelSerializer):
    product = StatePrimaryKeyRelatedField('active', model=models.Product)
    product__name = serializers.CharField(source='product.name',read_only=True)

    class Meta:
        model = models.Lot
        fields = '__all__'
