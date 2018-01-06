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
from django.utils.translation import ugettext as _

User = get_user_model()


class TalkSerializer(serializers.Serializer):
    talker = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        required=True
    )
    listener = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        required=True
    )
    content = serializers.CharField(max_length=20, min_length=5)

    def validate(self, attrs):
        if attrs['talker'] == attrs['listener']:
            raise serializers.ValidationError(
                _("listener can not be talker himself")
            )
        return attrs
