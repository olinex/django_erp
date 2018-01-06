#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2018/1/6 上午12:16
"""

__all__ = ['PermissionsSerializer']

from rest_framework import serializers
from django.contrib.auth.models import Permission

class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'