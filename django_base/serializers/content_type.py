#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午10:17
"""

__all__ = ['ContentTypeSerializer']

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

class ContentTypeSerializer(serializers.ModelSerializer):
    app_label = serializers.ReadOnlyField()
    model = serializers.ReadOnlyField()
    class Meta:
        model = ContentType
        fields = '__all__'