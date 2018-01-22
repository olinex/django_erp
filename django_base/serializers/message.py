#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午10:14
"""

__all__ = ['MessageSerializer']

from .. import models
from rest_framework import serializers
from django_erp.rest.serializers import ContentTypeSerializer

class MessageSerializer(serializers.ModelSerializer):
    creater = serializers.PrimaryKeyRelatedField(read_only=True)
    creater__avatar = serializers.ImageField(source='creater.avatar',read_only=True)
    creater__first_name = serializers.CharField(source='creater.first_name',read_only=True)
    creater__last_name = serializers.CharField(source='creater.last_name',read_only=True)
    content_type = ContentTypeSerializer(read_only=True)
    create_time = serializers.ReadOnlyField()
    object_id = serializers.ReadOnlyField()

    class Meta:
        model = models.Message
        fields = '__all__'