#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/19 上午12:01
"""

from rest_framework import serializers
from django_erp.rest.fields import StatePrimaryKeyRelatedField

class FollowSerializer(serializers.Serializer):
    followers = serializers.ListField
