#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午3:35
"""

__all__ = ['ChangeSerializer']


from .. import models
from rest_framework import serializers
from django_erp.rest.serializers import OrderModelSerializer,ContentTypeSerializer


class ChangeSerializer(OrderModelSerializer):
    before = serializers.ReadOnlyField()
    after = serializers.ReadOnlyField()
    creater = serializers.ReadOnlyField()
    content_type = ContentTypeSerializer(read_only=True)
    object_id = serializers.ReadOnlyField()

    class Meta:
        model = models.Change
        fields = '__all__'