#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午3:34
"""

__all__ = ['RegionSerializer']

from .. import models
from rest_framework import serializers
from django_erp.rest.fields import StatePrimaryKeyRelatedField
from django_erp.rest.serializers import DataModelSerializer


class RegionSerializer(DataModelSerializer):
    city = StatePrimaryKeyRelatedField('active',model=models.City)
    city__name = serializers.CharField(source='city.name',read_only=True)
    city__province = serializers.PrimaryKeyRelatedField(source='city.province',read_only=True)
    city__province__name = serializers.CharField(source='city.province.name',read_only=True)
    city__province__country = serializers.CharField(source='city.province.country',read_only=True)
    class Meta:
        model = models.Region
        fields = '__all__'