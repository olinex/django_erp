#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/17 下午9:47
"""

__all__ = ['ArgumentSerializer']

from .. import models
from rest_framework import serializers
from django_erp.rest.serializers import HistoryModelSerializer

class ArgumentSerializer(HistoryModelSerializer):
    form = serializers.ReadOnlyField()
    value = serializers.JSONField()

    class Meta:
        model = models.Argument
        exclude = ('followers',)