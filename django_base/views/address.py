#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午8:38
"""

__all__ = ['AddressViewSet']

from .. import models
from .. import serializers
from django_erp.rest.viewsets import PermMethodViewSet

class AddressViewSet(PermMethodViewSet):
    model = models.Address
    serializer_class = serializers.AddressSerializer