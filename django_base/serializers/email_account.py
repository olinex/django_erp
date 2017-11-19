#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午10:09
"""

__all__ = ['EmailAccountSerializer']

from .. import models
from rest_framework import serializers

class EmailAccountSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=models.User.objects.filter(is_active=True)
    )

    class Meta:
        model = models.EmailAccount
        fields = '__all__'