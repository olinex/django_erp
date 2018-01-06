#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午3:31
"""

__all__ = ['CitySerializer']

from .. import models
from rest_framework import serializers
from django_erp.rest.fields import StatePrimaryKeyRelatedField
from django_erp.rest.serializers import DataModelSerializer


class CitySerializer(DataModelSerializer):
    province = StatePrimaryKeyRelatedField('active',model=models.Province)
    province__name = serializers.CharField(source='province.name', read_only=True)
    province__country = serializers.CharField(source='province.country', read_only=True)
    
    class Meta:
        model = models.City
        fields = '__all__'