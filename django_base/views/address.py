#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午8:38
"""

__all__ = ['AddressViewSet']

from .. import models, serializers, filters
from django_erp.rest.viewsets import PermMethodViewSet

class AddressViewSet(PermMethodViewSet):
    model = models.Address
    serializer_class = serializers.AddressSerializer
    filter_class = filters.AddressFilter

    def get_queryset(self):
        return self.model.objects.select_related(
            'region',
            'region__city',
            'region__city__province'
        ).all()