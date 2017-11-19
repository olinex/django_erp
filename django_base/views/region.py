#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author:    olinex
@time:      2017/11/12 下午8:33
"""

__all__ = ['RegionViewSet']

from .. import models, serializers, filters
from django_erp.rest.viewsets import DataViewSet


class RegionViewSet(DataViewSet):
    model = models.Region
    serializer_class = serializers.RegionSerializer
    filter_class = filters.RegionFilter

    def get_queryset(self):
        return self.model.objects.select_related('city','city__province')