#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/24 下午4:14
"""

__all__ = ['AttributeSerializer']

from .. import models
from rest_framework import serializers
from django_erp.rest.serializers import HistoryModelSerializer

class AttributeSerializer(HistoryModelSerializer):
    value = serializers.ListField(
        child=serializers.CharField(min_length=3),
        min_length=1
    )

    class Meta:
        model = models.Attribute
        fields = '__all__'