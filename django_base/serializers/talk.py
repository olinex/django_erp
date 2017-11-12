#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/9 下午1:14
"""

__all__ = [
    'TalkSerializer',
]

from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class TalkSerializer(serializers.Serializer):
    talker = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))
    listener = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))
    content = serializers.CharField(max_length=20, min_length=5)
